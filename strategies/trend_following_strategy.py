"""Trend following strategy implementation."""

from typing import Optional, Dict
import pandas as pd
import logging
from strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class TrendFollowingStrategy(BaseStrategy):
    """Trend following strategy for long-term trend trades."""

    def __init__(self):
        super().__init__()
        self.name = "trend_following"
        self.display_name = "Trend Following"

    def analyze(self, df: pd.DataFrame, symbol: str, market: str,
                timeframe: str) -> Optional[Dict]:
        """Analyze for trend following signals."""
        if len(df) < 100:
            return None
        last = df.iloc[-1]
        prev = df.iloc[-2]

        long_conditions = 0
        short_conditions = 0
        total_conditions = 7

        # EMA alignment (20 > 50 > 200)
        ema20 = last.get("ema_20", 0)
        ema50 = last.get("ema_50", 0)
        ema200 = last.get("ema_200", 0)
        if ema20 > ema50 > ema200:
            long_conditions += 1
        if ema20 < ema50 < ema200:
            short_conditions += 1

        # ADX > 30
        adx = last.get("adx", 0)
        if adx > 30:
            long_conditions += 1
            short_conditions += 1

        # Price making new high/low
        price = last.get("close", 0)
        recent_high = df["high"].tail(20).max()
        recent_low = df["low"].tail(20).min()
        if price >= recent_high * 0.99:
            long_conditions += 1
        if price <= recent_low * 1.01:
            short_conditions += 1

        # RSI in range
        rsi = last.get("rsi", 50)
        if 50 < rsi < 80:
            long_conditions += 1
        if 20 < rsi < 50:
            short_conditions += 1

        # Volume increasing in trend direction
        if last.get("volume_ratio", 1) > 1.0:
            long_conditions += 1
            short_conditions += 1

        # Supertrend direction
        supertrend_dir = last.get("supertrend_direction", 0)
        if supertrend_dir == 1:
            long_conditions += 1
        if supertrend_dir == -1:
            short_conditions += 1

        # MACD positive/negative
        macd = last.get("macd", 0)
        if macd > 0:
            long_conditions += 1
        if macd < 0:
            short_conditions += 1

        confidence_long = self._calculate_confidence(long_conditions, total_conditions)
        confidence_short = self._calculate_confidence(short_conditions, total_conditions)

        entry_price = price
        atr = last.get("atr", entry_price * 0.02)
        supertrend = last.get("supertrend", entry_price)

        if confidence_long and long_conditions >= 5:
            sl = supertrend if supertrend < entry_price else entry_price - atr * 2
            return self._create_signal(
                "LONG", symbol, market, self.name, timeframe,
                entry_price, sl, take_profit_1=None,
                confidence=confidence_long
            )

        if confidence_short and short_conditions >= 5:
            sl = supertrend if supertrend > entry_price else entry_price + atr * 2
            return self._create_signal(
                "SHORT", symbol, market, self.name, timeframe,
                entry_price, sl, take_profit_1=None,
                confidence=confidence_short
            )

        return None

    def check_exit(self, df: pd.DataFrame, signal: Dict,
                   current_price: float) -> Optional[str]:
        """Check exit conditions for trend following."""
        last = df.iloc[-1] if len(df) > 0 else {}

        if signal["signal_type"] == "LONG":
            if current_price <= signal["stop_loss"]:
                return "SL_HIT"
            ema20 = last.get("ema_20", 0)
            ema50 = last.get("ema_50", 0)
            if ema20 < ema50 and ema20 > 0:
                return "TREND_BROKEN"
        else:
            if current_price >= signal["stop_loss"]:
                return "SL_HIT"
            ema20 = last.get("ema_20", 0)
            ema50 = last.get("ema_50", 0)
            if ema20 > ema50 and ema20 > 0:
                return "TREND_BROKEN"

        atr = last.get("atr", 0)
        trailing_distance = atr * 2 if atr > 0 else abs(signal["entry_price"] - signal["stop_loss"]) * 0.02

        if signal["signal_type"] == "LONG" and current_price > signal["entry_price"]:
            new_sl = current_price - trailing_distance
            if new_sl > signal["stop_loss"]:
                signal["stop_loss"] = new_sl
        elif signal["signal_type"] == "SHORT" and current_price < signal["entry_price"]:
            new_sl = current_price + trailing_distance
            if new_sl < signal["stop_loss"]:
                signal["stop_loss"] = new_sl

        return None
