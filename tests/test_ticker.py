import sys
from unittest.mock import MagicMock, patch

import ticker


def make_mock_stock(last_price, prev_close, news=None):
    stock = MagicMock()
    stock.fast_info = {"lastPrice": last_price, "previousClose": prev_close}
    stock.news = news or []
    return stock


class TestPrintStock:
    def test_prints_price_and_up_arrow_on_gain(self, capsys):
        stock = make_mock_stock(105.0, 100.0)
        with patch("ticker.yf.Ticker", return_value=stock):
            ticker.print_stock("AAPL")
        out = capsys.readouterr().out
        assert "AAPL" in out
        assert "$105.00" in out
        assert "^ +5.00 (+5.00%)" in out

    def test_prints_down_arrow_on_loss(self, capsys):
        stock = make_mock_stock(95.0, 100.0)
        with patch("ticker.yf.Ticker", return_value=stock):
            ticker.print_stock("AAPL")
        out = capsys.readouterr().out
        assert "v -5.00 (-5.00%)" in out

    def test_limits_news_to_three_items(self, capsys):
        news = [
            {"content": {"title": f"Headline {i}", "provider": {"displayName": "Src"}}}
            for i in range(5)
        ]
        stock = make_mock_stock(100.0, 100.0, news=news)
        with patch("ticker.yf.Ticker", return_value=stock):
            ticker.print_stock("AAPL")
        out = capsys.readouterr().out
        assert out.count("Headline") == 3
        assert "Headline 3" not in out

    def test_falls_back_when_no_content_key(self, capsys):
        news = [{"title": "Bare headline", "provider": {"displayName": "Src"}}]
        stock = make_mock_stock(100.0, 100.0, news=news)
        with patch("ticker.yf.Ticker", return_value=stock):
            ticker.print_stock("AAPL")
        out = capsys.readouterr().out
        assert "Bare headline (Src)" in out

    def test_missing_title_and_publisher_use_defaults(self, capsys):
        news = [{"content": {}}]
        stock = make_mock_stock(100.0, 100.0, news=news)
        with patch("ticker.yf.Ticker", return_value=stock):
            ticker.print_stock("AAPL")
        out = capsys.readouterr().out
        assert "Untitled (Unknown source)" in out


class TestMain:
    def test_uses_default_tickers_when_no_args(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["ticker.py"])
        called = []
        monkeypatch.setattr(ticker, "print_stock", lambda s: called.append(s))
        ticker.main()
        assert called == ticker.DEFAULT_TICKERS

    def test_uses_and_uppercases_cli_args(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["ticker.py", "aapl", "tsla"])
        called = []
        monkeypatch.setattr(ticker, "print_stock", lambda s: called.append(s))
        ticker.main()
        assert called == ["AAPL", "TSLA"]

    def test_continues_after_failure(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["ticker.py", "GOOD", "BAD"])

        def fake_print_stock(symbol):
            if symbol == "BAD":
                raise ValueError("boom")

        monkeypatch.setattr(ticker, "print_stock", fake_print_stock)
        ticker.main()
        out = capsys.readouterr().out
        assert "BAD: failed to fetch (boom)" in out
