"""Thin wrapper around OpenAI's embeddings API - used only for turning saved
notes/articles and questions into vectors for the RAG store. Chat still goes
through DeepSeek (deepseek_client.py); DeepSeek doesn't expose an embeddings
endpoint (checked api-docs.deepseek.com - chat/completions only), so this
needs its own key and provider.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"

# per openai.com/api/pricing (checked July 2026)
PRICE_PER_MILLION_TOKENS = 0.02


@dataclass
class EmbedResult:
    vectors: list[np.ndarray]
    total_tokens: int

    @property
    def estimated_cost_usd(self) -> float:
        return (self.total_tokens / 1_000_000) * PRICE_PER_MILLION_TOKENS


def get_client() -> OpenAI:
    api_key = os.environ["OPENAI_API_KEY"]
    return OpenAI(api_key=api_key)


def embed(texts: list[str]) -> EmbedResult:
    client = get_client()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)

    # normalize so a plain dot product (FAISS IndexFlatIP) gives cosine similarity
    vectors = []
    for item in response.data:
        vec = np.array(item.embedding, dtype="float32")
        norm = np.linalg.norm(vec)
        vectors.append(vec / norm if norm > 0 else vec)

    return EmbedResult(vectors=vectors, total_tokens=response.usage.total_tokens)
