from unittest.mock import patch

import app


def test_index_renders_all_tickers_and_disables_caching():
    with patch("app.format_stock", side_effect=lambda symbol: f"{symbol} report"):
        client = app.app.test_client()
        response = client.get("/")

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    body = response.get_data(as_text=True)
    for symbol in app.APP_TICKERS:
        assert f"{symbol} report" in body


def test_index_shows_failure_message_for_broken_ticker():
    def fake_format_stock(symbol):
        if symbol == "MSFT":
            raise ValueError("boom")
        return f"{symbol} ok"

    with patch("app.format_stock", side_effect=fake_format_stock):
        client = app.app.test_client()
        response = client.get("/")

    body = response.get_data(as_text=True)
    assert "MSFT: failed to fetch (boom)" in body
    assert "AAPL ok" in body
