"""Tests for trading strategies."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime
from core.indicator_engine import IndicatorEngine
from strategies.scalping_strategy import ScalpingStrategy
from strategies.day_trading_strategy import DayTradingStrategy
from strategies.swing_trading_strategy import SwingTradingStrategy
from strategies.trend_following_strategy import TrendFollowingStrategy


class TestStrategies:
    """Test trading strategies."""

    def setup_method(self):
        self.engine = IndicatorEngine()
        self.df = self._create_test_data(200)
        self.df = self.engine.calculate_all(self.df)

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

    def test_scalping_strategy(self):
        """Test scalping strategy."""
        strategy = ScalpingStrategy()
        assert strategy.name == "scalping"
        signal = strategy.analyze(self.df, "BTCUSDT", "crypto", "15m")
        if signal:
            assert signal["signal_type"] in ["LONG", "SHORT"]
            assert signal["entry_price"] > 0
            assert signal["stop_loss"] > 0
            assert signal["symbol"] == "BTCUSDT"

    def test_day_trading_strategy(self):
        """Test day trading strategy."""
        strategy = DayTradingStrategy()
        assert strategy.name == "day_trading"
        signal = strategy.analyze(self.df, "BTCUSDT", "crypto", "15m")
        if signal:
            assert signal["signal_type"] in ["LONG", "SHORT"]
            assert signal["entry_price"] > 0

    def test_swing_strategy(self):
        """Test swing trading strategy."""
        strategy = SwingTradingStrategy()
        assert strategy.name == "swing"
        signal = strategy.analyze(self.df, "BTCUSDT", "crypto", "15m")
        if signal:
            assert signal["signal_type"] in ["LONG", "SHORT"]

    def test_trend_following_strategy(self):
        """Test trend following strategy."""
        strategy = TrendFollowingStrategy()
        assert strategy.name == "trend_following"
        signal = strategy.analyze(self.df, "BTCUSDT", "crypto", "15m")
        if signal:
            assert signal["signal_type"] in ["LONG", "SHORT"]

    def test_confidence_calculation(self):
        """Test confidence calculation."""
        strategy = ScalpingStrategy()
        assert strategy._calculate_confidence(6, 6) == "HIGH"
        assert strategy._calculate_confidence(5, 6) == "HIGH"
        assert strategy._calculate_confidence(4, 6) == "MEDIUM"
        assert strategy._calculate_confidence(3, 6) == "LOW"
        assert strategy._calculate_confidence(2, 6) is None

    def test_swing_levels(self):
        """Test swing high/low calculation."""
        strategy = ScalpingStrategy()
        swing_low = strategy._find_swing_low(self.df, 10)
        swing_high = strategy._find_swing_high(self.df, 10)
        assert swing_low <= self.df["low"].tail(10).max()
        assert swing_high >= self.df["high"].tail(10).min()

    def test_signal_creation(self):
        """Test signal creation."""
        strategy = ScalpingStrategy()
        signal = strategy._create_signal(
            "LONG", "BTCUSDT", "crypto", "scalping", "15m",
            64000, 63500, 64500, 65000, confidence="HIGH"
        )
        assert signal["signal_type"] == "LONG"
        assert signal["symbol"] == "BTCUSDT"
        assert signal["entry_price"] == 64000
        assert signal["stop_loss"] == 63500
        assert signal["take_profit_1"] == 64500
        assert signal["risk_reward_ratio"] > 0

    def test_exit_conditions(self):
        """Test exit condition checks."""
        strategy = ScalpingStrategy()
        signal = {
            "signal_type": "LONG",
            "entry_price": 64000,
            "stop_loss": 63500,
            "take_profit_1": 64500,
        }
        assert strategy.check_exit(self.df, signal, 63400) == "SL_HIT"
        assert strategy.check_exit(self.df, signal, 64600) == "TP1_HIT"
        assert strategy.check_exit(self.df, signal, 64100) is None


if __name__ == "__main__":
    test = TestStrategies()
    test.setup_method()
    try:
        test.test_scalping_strategy()
        test.test_day_trading_strategy()
        test.test_swing_strategy()
        test.test_trend_following_strategy()
        test.test_confidence_calculation()
        test.test_swing_levels()
        test.test_signal_creation()
        test.test_exit_conditions()
        print("All strategy tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
