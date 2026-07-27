"""Local RAG store - save articles / portfolio notes, pull back the most
relevant ones for a question.

Retrieval used to be plain TF-IDF cosine similarity (sklearn) - decent for
keyword overlap, but it missed anything phrased differently from what's
saved. Swapped in real vector search instead: OpenAI embeddings (no local
model to download, which is what killed a sentence-transformers attempt
here before) plus a FAISS index for the actual similarity search.

Embeddings are cached on each document and computed once, not re-fit on
every query like the old TF-IDF matrix was - unlike TF-IDF, every call here
costs real (if tiny) money, so there's no point re-embedding unchanged notes
on every question.
"""
from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np

from embeddings_client import embed

DATA_FILE = Path(__file__).resolve().parent / "data" / "rag_documents.json"
EMBEDDING_DIM = 1536  # text-embedding-3-small

# empirical cutoff - unrelated text still scores well above 0 on cosine
# similarity with these embeddings, so a straight ">0" filter (like the old
# TF-IDF one) let everything through regardless of relevance
MIN_SIMILARITY = 0.2


class RagStore:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.documents: list[dict] = []
        self.embedding_tokens = 0
        self.embedding_cost_usd = 0.0
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self.documents = json.loads(self.path.read_text(encoding="utf-8"))

        # docs saved before the embeddings upgrade won't have a vector yet -
        # backfill them once here instead of needing a separate migration script
        backfilled = False
        for doc in self.documents:
            if "embedding" not in doc:
                result = embed([doc["text"]])
                doc["embedding"] = result.vectors[0].tolist()
                self.embedding_tokens += result.total_tokens
                self.embedding_cost_usd += result.estimated_cost_usd
                backfilled = True
        if backfilled:
            self._save()

        self._rebuild_index()

    def _rebuild_index(self) -> None:
        self.index = faiss.IndexFlatIP(EMBEDDING_DIM)
        if self.documents:
            vectors = np.array([doc["embedding"] for doc in self.documents], dtype="float32")
            self.index.add(vectors)

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.documents, indent=2), encoding="utf-8")

    def add_document(self, text: str, source: str, ticker: str | None = None) -> None:
        result = embed([text])
        self.embedding_tokens += result.total_tokens
        self.embedding_cost_usd += result.estimated_cost_usd
        vector = result.vectors[0].tolist()

        if source == "portfolio" and ticker:
            # re-saving a holding for a ticker you already have should update
            # it in place, not pile up duplicate entries every time you tweak
            # the share count
            self.documents = [
                doc
                for doc in self.documents
                if not (doc["source"] == "portfolio" and doc.get("ticker") == ticker)
            ]
            self.documents.append(
                {"text": text, "source": source, "ticker": ticker, "embedding": vector}
            )
        else:
            self.documents.append({"text": text, "source": source, "embedding": vector})

        self._save()
        self._rebuild_index()

    def remove_document(self, index: int) -> None:
        del self.documents[index]
        self._save()
        self._rebuild_index()

    def retrieve(self, query: str, top_k: int = 8) -> list[dict]:
        if not self.documents:
            return []

        result = embed([query])
        self.embedding_tokens += result.total_tokens
        self.embedding_cost_usd += result.estimated_cost_usd
        query_vector = result.vectors[0].reshape(1, -1)

        k = min(top_k, len(self.documents))
        scores, indices = self.index.search(query_vector, k)

        matches = []
        for score, i in zip(scores[0], indices[0]):
            if i == -1 or score <= MIN_SIMILARITY:
                continue
            doc = {key: value for key, value in self.documents[i].items() if key != "embedding"}
            doc["score"] = float(score)
            matches.append(doc)
        return matches
