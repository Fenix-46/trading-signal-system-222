"""Tests for indicator engine."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.indicator_engine import IndicatorEngine


class TestIndicators:
    """Test indicator calculations."""

    def setup_method(self):
        self.engine = IndicatorEngine()
        self.df = self._create_test_data()

    def _create_test_data(self, rows=200):
        """Create test OHLCV data."""
        np.random.seed(42)
        dates = pd.date_range(end=datetime.now(), periods=rows, freq="15min")
        base = 64000
        returns = np.random.normal(0.0001, 0.01, rows)
        prices = base * np.exp(np.cumsum(returns))
        df = pd.DataFrame({
            "open": prices * (1 + np.random.uniform(-0.005, 0.005, rows)),
            "high": prices * (1 + np.abs(np.random.normal(0, 0.01, rows))),
            "low": prices * (1 - np.abs(np.random.normal(0, 0.01, rows))),
            "close": prices,
            "volume": np.random.uniform(1000, 100000, rows),
        }, index=dates)
        return df

    def test_calculate_all(self):
        """Test all indicators calculation."""
        result = self.engine.calculate_all(self.df)
        assert result is not None
        assert not result.empty
        assert "ema_9" in result.columns
        assert "rsi" in result.columns
        assert "macd" in result.columns
        assert "bb_upper" in result.columns
        assert "stoch_k" in result.columns
        assert "adx" in result.columns
        assert "atr" in result.columns
        assert "supertrend" in result.columns

    def test_ema(self):
        """Test EMA calculation."""
        result = self.engine._ema(self.df.copy())
        assert "ema_9" in result.columns
        assert "ema_21" in result.columns
        assert "ema_50" in result.columns
        assert result["ema_9"].notna().sum() > 0

    def test_rsi(self):
        """Test RSI calculation."""
        result = self.engine._rsi(self.df.copy())
        assert "rsi" in result.columns
        rsi_valid = result["rsi"].dropna()
        assert all(0 <= v <= 100 for v in rsi_valid)

    def test_macd(self):
        """Test MACD calculation."""
        result = self.engine._macd(self.df.copy())
        assert "macd" in result.columns
        assert "macd_signal" in result.columns
        assert "macd_histogram" in result.columns

    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        result = self.engine._bollinger_bands(self.df.copy())
        assert "bb_upper" in result.columns
        assert "bb_lower" in result.columns
        valid = result.dropna()
        assert all(valid["bb_upper"] >= valid["bb_lower"])

    def test_stochastic(self):
        """Test Stochastic calculation."""
        result = self.engine._stochastic(self.df.copy())
        assert "stoch_k" in result.columns
        assert "stoch_d" in result.columns
        valid = result["stoch_k"].dropna()
        assert all(0 <= v <= 100 for v in valid)

    def test_adx(self):
        """Test ADX calculation."""
        result = self.engine._adx(self.df.copy())
        assert "adx" in result.columns
        valid = result["adx"].dropna()
        assert all(v >= 0 for v in valid)

    def test_atr(self):
        """Test ATR calculation."""
        result = self.engine._atr(self.df.copy())
        assert "atr" in result.columns
        valid = result["atr"].dropna()
        assert all(v >= 0 for v in valid)

    def test_supertrend(self):
        """Test Supertrend calculation."""
        result = self.engine._atr(self.df.copy())
        result = self.engine._supertrend(result)
        assert "supertrend" in result.columns
        assert "supertrend_direction" in result.columns

    def test_get_latest_indicators(self):
        """Test getting latest indicators."""
        result = self.engine.calculate_all(self.df)
        indicators = self.engine.get_latest_indicators(result)
        assert "close" in indicators
        assert "rsi" in indicators
        assert "macd" in indicators
        assert "adx" in indicators

    def test_empty_data(self):
        """Test with empty data."""
        result = self.engine.calculate_all(pd.DataFrame())
        assert result is None

    def test_insufficient_data(self):
        """Test with insufficient data."""
        small_df = self.df.head(10)
        result = self.engine.calculate_all(small_df)
        assert result is None


if __name__ == "__main__":
    test = TestIndicators()
    test.setup_method()
    try:
        test.test_calculate_all()
        test.test_ema()
        test.test_rsi()
        test.test_macd()
        test.test_bollinger_bands()
        test.test_stochastic()
        test.test_adx()
        test.test_atr()
        test.test_supertrend()
        test.test_get_latest_indicators()
        test.test_empty_data()
        test.test_insufficient_data()
        print("All indicator tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
