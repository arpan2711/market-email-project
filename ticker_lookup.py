"""Look up a ticker's full company name so portfolio notes match on both
"AAPL" and "Apple" - TF-IDF retrieval is a plain word match, so a question
about "Nvidia" won't hit a doc that only ever says "NVDA".
"""
from __future__ import annotations

import yfinance as yf


def company_name(ticker: str) -> str | None:
    try:
        info = yf.Ticker(ticker).info
        return info.get("longName") or info.get("shortName")
    except Exception:
        # bad ticker, no internet, yfinance having a bad day - not worth
        # failing the whole save over, just fall back to the ticker alone
        return None
