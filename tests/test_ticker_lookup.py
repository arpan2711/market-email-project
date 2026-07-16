from unittest.mock import MagicMock, patch

import ticker_lookup


def test_company_name_returns_long_name():
    fake_ticker = MagicMock()
    fake_ticker.info = {"longName": "NVIDIA Corporation", "shortName": "NVIDIA"}

    with patch("ticker_lookup.yf.Ticker", return_value=fake_ticker):
        assert ticker_lookup.company_name("NVDA") == "NVIDIA Corporation"


def test_company_name_falls_back_to_short_name():
    fake_ticker = MagicMock()
    fake_ticker.info = {"longName": None, "shortName": "NVIDIA"}

    with patch("ticker_lookup.yf.Ticker", return_value=fake_ticker):
        assert ticker_lookup.company_name("NVDA") == "NVIDIA"


def test_company_name_returns_none_on_failure():
    with patch("ticker_lookup.yf.Ticker", side_effect=Exception("network error")):
        assert ticker_lookup.company_name("BOGUS") is None
