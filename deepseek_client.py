"""Thin wrapper around the DeepSeek chat API - it's OpenAI-compatible so we
just point the normal openai client at their base url.
"""
from __future__ import annotations

import os

from openai import OpenAI

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"
# MODEL = "deepseek-reasoner"  # reasoning model, slower, didn't need it here


def get_client() -> OpenAI:
    api_key = os.environ["DEEPSEEK_API_KEY"]
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def ask(question: str, context_docs: list[dict]) -> str:
    if context_docs:
        context_text = "\n\n".join(f"[{doc['source']}] {doc['text']}" for doc in context_docs)
    else:
        context_text = "No saved articles or portfolio notes match this question."

    system_prompt = (
        "You are a helpful assistant answering questions using the user's own "
        "saved articles and stock portfolio notes below. If the context doesn't "
        "answer the question, say so instead of guessing.\n\n"
        f"Context:\n{context_text}"
    )

    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    # print(response)  # useful when debugging prompts, noisy otherwise
    return response.choices[0].message.content
