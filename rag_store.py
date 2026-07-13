"""Tiny local RAG store - save articles / portfolio notes, pull back the most
relevant ones for a question.

capstone used FAISS + Azure OpenAI embeddings for this. no azure key here
though, just deepseek. tried keeping FAISS and swapping in sentence-transformers
for local embeddings instead:

    # from sentence_transformers import SentenceTransformer
    # import faiss
    #
    # _model = SentenceTransformer("all-MiniLM-L6-v2")
    #
    # class FaissStore:
    #     def __init__(self):
    #         self.index = faiss.IndexFlatIP(384)
    #         self.docs = []
    #
    #     def add(self, text, source):
    #         vec = _model.encode([text], normalize_embeddings=True)
    #         self.index.add(vec)
    #         self.docs.append({"text": text, "source": source})
    #
    #     def search(self, query, k=4):
    #         vec = _model.encode([query], normalize_embeddings=True)
    #         scores, idx = self.index.search(vec, k)
    #         return [self.docs[i] for i in idx[0] if i != -1]

but the model download took forever just for a handful of docs. going with
plain TF-IDF cosine similarity below instead - way lighter, good enough at
this scale.
"""
from __future__ import annotations

import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_FILE = Path(__file__).resolve().parent / "data" / "rag_documents.json"


class RagStore:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.documents: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self.documents = json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.documents, indent=2), encoding="utf-8")

    def add_document(self, text: str, source: str) -> None:
        self.documents.append({"text": text, "source": source})
        self._save()

    def retrieve(self, query: str, top_k: int = 4) -> list[dict]:
        if not self.documents:
            return []

        corpus = [doc["text"] for doc in self.documents]
        vectorizer = TfidfVectorizer(stop_words="english")
        # refitting on every call - fine for a personal, small doc set
        matrix = vectorizer.fit_transform(corpus + [query])
        similarities = cosine_similarity(matrix[-1], matrix[:-1])[0]

        ranked = sorted(range(len(self.documents)), key=lambda i: similarities[i], reverse=True)
        return [self.documents[i] for i in ranked[:top_k] if similarities[i] > 0]
