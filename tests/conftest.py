import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import numpy as np

from embeddings_client import EmbedResult

# shared fake for rag_store's real (1536-dim) OpenAI embeddings - hashes each
# word into a bag-of-words style vector so texts sharing vocabulary come out
# genuinely similar, which is enough to exercise ranking without a real
# OPENAI_API_KEY or network call
EMBEDDING_DIM = 1536


def fake_vector(text: str) -> np.ndarray:
    vec = np.zeros(EMBEDDING_DIM, dtype="float32")
    for word in text.lower().split():
        vec[hash(word) % EMBEDDING_DIM] += 1.0
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def fake_embed(texts: list[str]) -> EmbedResult:
    return EmbedResult(vectors=[fake_vector(t) for t in texts], total_tokens=10 * len(texts))
