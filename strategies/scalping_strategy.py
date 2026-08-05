"""Scalping strategy implementation."""

from typing import Optional, Dict
import pandas as pd
import logging
from strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class ScalpingStrategy(BaseStrategy):
    """Scalping strategy for short-term trades."""

    def __init__(self):
        super().__init__()
        self.name = "scalping"
        self.display_name = "Scalping"

    def analyze(self, df: pd.DataFrame, symbol: str, market: str,
                timeframe: str) -> Optional[Dict]:
        """Analyze for scalping signals."""
        if len(df) < 30:
            return None
        last = df.iloc[-1]
        prev = df.iloc[-2]

        long_conditions = 0
        short_conditions = 0
        total_conditions = 6

        # EMA crossover
        if last.get("ema_9", 0) > last.get("ema_21", 0):
            long_conditions += 1
        if last.get("ema_9", 0) < last.get("ema_21", 0):
            short_conditions += 1

        # RSI
        rsi = last.get("rsi", 50)
        if prev.get("rsi", 50) <= 30 and rsi > 30:
            long_conditions += 1
        if prev.get("rsi", 50) >= 70 and rsi < 70:
            short_conditions += 1

        # MACD histogram crossover
        if prev.get("macd_histogram", 0) <= 0 and last.get("macd_histogram", 0) > 0:
            long_conditions += 1
        if prev.get("macd_histogram", 0) >= 0 and last.get("macd_histogram", 0) < 0:
            short_conditions += 1

        # Volume above average
        if last.get("volume_ratio", 1) > 1.0:
            long_conditions += 1
            short_conditions += 1

        # Bollinger Band bounce
        if last.get("close", 0) <= last.get("bb_lower", 0) * 1.002:
            long_conditions += 1
        if last.get("close", 0) >= last.get("bb_upper", 0) * 0.998:
            short_conditions += 1

        # Stochastic
        if (prev.get("stoch_k", 50) < prev.get("stoch_d", 50) and
            last.get("stoch_k", 50) > last.get("stoch_d", 50) and
            last.get("stoch_k", 50) < 20):
            long_conditions += 1
        if (prev.get("stoch_k", 50) > prev.get("stoch_d", 50) and
            last.get("stoch_k", 50) < last.get("stoch_d", 50) and
            last.get("stoch_k", 50) > 80):
            short_conditions += 1

        confidence_long = self._calculate_confidence(long_conditions, total_conditions)
        confidence_short = self._calculate_confidence(short_conditions, total_conditions)

        entry_price = last.get("close", 0)
        atr = last.get("atr", entry_price * 0.005)

        if confidence_long and long_conditions >= 4:
            sl = self._find_swing_low(df, 10)
            if sl >= entry_price:
                sl = entry_price - atr * 1.5
            tp1 = entry_price + abs(entry_price - sl)
            tp2 = entry_price + abs(entry_price - sl) * 1.5
            return self._create_signal(
                "LONG", symbol, market, self.name, timeframe,
                entry_price, sl, tp1, tp2, confidence=confidence_long
            )

        if confidence_short and short_conditions >= 4:
            sl = self._find_swing_high(df, 10)
            if sl <= entry_price:
                sl = entry_price + atr * 1.5
            tp1 = entry_price - abs(sl - entry_price)
            tp2 = entry_price - abs(sl - entry_price) * 1.5
            return self._create_signal(
                "SHORT", symbol, market, self.name, timeframe,
                entry_price, sl, tp1, tp2, confidence=confidence_short
            )

        return None

    def check_exit(self, df: pd.DataFrame, signal: Dict,
                   current_price: float) -> Optional[str]:
        """Check exit conditions for scalping."""
        if signal["signal_type"] == "LONG":
            if current_price <= signal["stop_loss"]:
                return "SL_HIT"
            if signal.get("take_profit_1") and current_price >= signal["take_profit_1"]:
                return "TP1_HIT"
        else:
            if current_price >= signal["stop_loss"]:
                return "SL_HIT"
            if signal.get("take_profit_1") and current_price <= signal["take_profit_1"]:
                return "TP1_HIT"

        trailing = abs(signal["entry_price"] - signal["stop_loss"]) * 0.003
        if signal["signal_type"] == "LONG" and current_price > signal["entry_price"]:
            new_sl = current_price - trailing
            if new_sl > signal["stop_loss"]:
                signal["stop_loss"] = new_sl
        elif signal["signal_type"] == "SHORT" and current_price < signal["entry_price"]:
            new_sl = current_price + trailing
            if new_sl < signal["stop_loss"]:
                signal["stop_loss"] = new_sl

        return None
