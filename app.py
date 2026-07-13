"""Local-only page showing live stock info. Hit refresh to pull fresh data.

Usage:
    python app.py
    then open http://127.0.0.1:5000 and hit refresh (F5) to update.
"""
from __future__ import annotations

from flask import Flask, Response

from ticker import format_stock

APP_TICKERS = ["AAPL", "MSFT", "GOOGL"]

app = Flask(__name__)

PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Stock Ticker</title>
<style>
  body {{
    background: #000;
    color: #0f0;
    font-family: Consolas, monospace;
    padding: 2rem;
  }}
  pre {{
    white-space: pre-wrap;
    font-size: 1.1rem;
  }}
</style>
</head>
<body>
<pre>{content}</pre>
</body>
</html>"""


def build_report() -> str:
    blocks = []
    for symbol in APP_TICKERS:
        try:
            blocks.append(format_stock(symbol))
        except Exception as exc:
            blocks.append(f"{symbol}: failed to fetch ({exc})")
    return "\n\n".join(blocks)


@app.route("/")
def index() -> Response:
    response = Response(PAGE.format(content=build_report()), mimetype="text/html")
    response.headers["Cache-Control"] = "no-store"
    return response


if __name__ == "__main__":
    app.run(debug=False)
