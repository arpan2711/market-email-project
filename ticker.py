"""Simple stock price and news ticker.

Usage:
    python ticker.py AAPL MSFT TSLA
    python ticker.py            # uses DEFAULT_TICKERS below
"""
from __future__ import annotations

import sys

import yfinance as yf

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_TICKERS = ["AAPL", "MSFT", "TSLA"]
NEWS_PER_TICKER = 3


def format_stock(symbol: str) -> str:
    stock = yf.Ticker(symbol)
    info = stock.fast_info

    price = info.get("lastPrice")
    prev_close = info.get("previousClose")
    change = price - prev_close
    pct_change = (change / prev_close) * 100

    arrow = "^" if change >= 0 else "v"
    lines = [
        f"{symbol}  ${price:,.2f}  {arrow} {change:+.2f} ({pct_change:+.2f}%)",
        "-" * 40,
    ]
    for item in stock.news[:NEWS_PER_TICKER]:
        content = item.get("content", item)
        title = content.get("title", "Untitled")
        publisher = content.get("provider", {}).get("displayName", "Unknown source")
        lines.append(f"  - {title} ({publisher})")
    return "\n".join(lines)


def print_stock(symbol: str) -> None:
    print(f"\n{format_stock(symbol)}")


def main() -> None:
    tickers = sys.argv[1:] or DEFAULT_TICKERS
    for symbol in tickers:
        try:
            print_stock(symbol.upper())
        except Exception as exc:
            print(f"\n{symbol}: failed to fetch ({exc})")


if __name__ == "__main__":
    main()
