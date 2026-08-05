"""Tests for data fetcher."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import DataFetcher


class TestDataFetcher:
    """Test data fetcher functionality."""

    def setup_method(self):
        self.fetcher = DataFetcher()

    def test_mock_data_generation(self):
        """Test mock data generation."""
        df = self.fetcher._generate_mock_data("BTCUSDT", "15m", 100)
        assert df is not None
        assert len(df) == 100
        assert "open" in df.columns
        assert "high" in df.columns
        assert "low" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns

    def test_mock_data_prices(self):
        """Test mock data has reasonable prices."""
        df = self.fetcher._generate_mock_data("BTCUSDT", "15m", 100)
        assert df["close"].mean() > 1000
        assert df["high"].max() >= df["close"].max()
        assert df["low"].min() <= df["close"].min()

    def test_base_price(self):
        """Test base price lookup."""
        assert self.fetcher._get_base_price("BTCUSDT") == 64000
        assert self.fetcher._get_base_price("ETHUSDT") == 3400
        assert self.fetcher._get_base_price("EURUSD") == 1.0850
        assert self.fetcher._get_base_price("AAPL") == 178

    def test_timeframe_conversion(self):
        """Test timeframe conversion."""
        assert self.fetcher._convert_timeframe_ccxt("15m") == "15m"
        assert self.fetcher._convert_timeframe_ccxt("1D") == "1d"
        assert self.fetcher._convert_timeframe_yfinance("15m") == "15m"
        assert self.fetcher._convert_timeframe_yfinance("4h") == "1h"

    def test_cache(self):
        """Test caching mechanism."""
        key = "test:symbol:15m"
        self.fetcher._cache[key] = "test_data"
        self.fetcher._cache_time[key] = __import__("time").time()
        assert self.fetcher._is_cache_valid(key)

    def test_fetch_with_mock(self):
        """Test fetch returns mock data when API fails."""
        df = self.fetcher.fetch_ohlcv("BTCUSDT", "15m", "crypto", limit=100)
        assert df is not None
        assert len(df) > 0


if __name__ == "__main__":
    test = TestDataFetcher()
    test.setup_method()
    try:
        test.test_mock_data_generation()
        test.test_mock_data_prices()
        test.test_base_price()
        test.test_timeframe_conversion()
        test.test_cache()
        test.test_fetch_with_mock()
        print("All data fetcher tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
