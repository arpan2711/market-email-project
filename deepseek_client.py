"""Thin wrapper around the DeepSeek chat API - it's OpenAI-compatible so we
just point the normal openai client at their base url.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# deepseek-chat/deepseek-reasoner get retired 2026-07-24, moved over to the
# v4 model names ahead of that instead of waiting for it to break
MODEL = "deepseek-v4-flash"
# MODEL = "deepseek-chat"  # old name, still works until the cutoff

# per api-docs.deepseek.com/quick_start/pricing (checked July 2026) - using
# the cache-miss input rate since we can't tell from here whether a given
# request hits their prompt cache, so this is a worst-case estimate
PRICE_PER_MILLION_INPUT_TOKENS = 0.14
PRICE_PER_MILLION_OUTPUT_TOKENS = 0.28


@dataclass
class ChatResult:
    answer: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    @property
    def estimated_cost_usd(self) -> float:
        input_cost = (self.prompt_tokens / 1_000_000) * PRICE_PER_MILLION_INPUT_TOKENS
        output_cost = (self.completion_tokens / 1_000_000) * PRICE_PER_MILLION_OUTPUT_TOKENS
        return input_cost + output_cost


def get_client() -> OpenAI:
    api_key = os.environ["DEEPSEEK_API_KEY"]
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def ask(question: str, context_docs: list[dict]) -> ChatResult:
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

    usage = response.usage
    return ChatResult(
        answer=response.choices[0].message.content,
        prompt_tokens=usage.prompt_tokens,
        completion_tokens=usage.completion_tokens,
        total_tokens=usage.total_tokens,
    )
