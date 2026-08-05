"""Swing trading strategy implementation."""

from typing import Optional, Dict
import pandas as pd
import logging
from strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class SwingTradingStrategy(BaseStrategy):
    """Swing trading strategy for multi-day trades."""

    def __init__(self):
        super().__init__()
        self.name = "swing"
        self.display_name = "Swing Trading"

    def analyze(self, df: pd.DataFrame, symbol: str, market: str,
                timeframe: str) -> Optional[Dict]:
        """Analyze for swing trading signals."""
        if len(df) < 100:
            return None
        last = df.iloc[-1]
        prev = df.iloc[-2]

        long_conditions = 0
        short_conditions = 0
        total_conditions = 7

        # EMA 50 > EMA 200 (uptrend)
        if last.get("ema_50", 0) > last.get("ema_200", 0):
            long_conditions += 1
        if last.get("ema_50", 0) < last.get("ema_200", 0):
            short_conditions += 1

        # Price near EMA 50 (pullback)
        ema50 = last.get("ema_50", 0)
        price = last.get("close", 0)
        if ema50 > 0:
            distance = abs(price - ema50) / ema50 * 100
            if distance < 1.0:
                if price > ema50:
                    long_conditions += 1
                else:
                    short_conditions += 1

        # RSI in support/resistance zone
        rsi = last.get("rsi", 50)
        if 40 <= rsi <= 60:
            long_conditions += 1
            short_conditions += 1

        # MACD histogram turning
        if (last.get("macd_histogram", 0) > prev.get("macd_histogram", 0) and
            last.get("macd_histogram", 0) < 0):
            long_conditions += 1
        if (last.get("macd_histogram", 0) < prev.get("macd_histogram", 0) and
            last.get("macd_histogram", 0) > 0):
            short_conditions += 1

        # Stochastic crossover
        stoch_k = last.get("stoch_k", 50)
        stoch_d = last.get("stoch_d", 50)
        prev_k = prev.get("stoch_k", 50)
        prev_d = prev.get("stoch_d", 50)
        if prev_k < prev_d and stoch_k > stoch_d and stoch_k < 30:
            long_conditions += 1
        if prev_k > prev_d and stoch_k < stoch_d and stoch_k > 70:
            short_conditions += 1

        # ADX > 20
        if last.get("adx", 0) > 20:
            long_conditions += 1
            short_conditions += 1

        # Volume pattern
        if last.get("volume_ratio", 1) > 1.0:
            long_conditions += 1
            short_conditions += 1

        confidence_long = self._calculate_confidence(long_conditions, total_conditions)
        confidence_short = self._calculate_confidence(short_conditions, total_conditions)

        entry_price = price
        atr = last.get("atr", entry_price * 0.02)

        if confidence_long and long_conditions >= 5:
            sl = self._find_swing_low(df, 30)
            if sl >= entry_price:
                sl = entry_price - atr * 3
            risk = entry_price - sl
            tp1 = entry_price + risk * 2
            tp2 = entry_price + risk * 3
            tp3 = entry_price + risk * 4
            return self._create_signal(
                "LONG", symbol, market, self.name, timeframe,
                entry_price, sl, tp1, tp2, tp3, confidence=confidence_long
            )

        if confidence_short and short_conditions >= 5:
            sl = self._find_swing_high(df, 30)
            if sl <= entry_price:
                sl = entry_price + atr * 3
            risk = sl - entry_price
            tp1 = entry_price - risk * 2
            tp2 = entry_price - risk * 3
            tp3 = entry_price - risk * 4
            return self._create_signal(
                "SHORT", symbol, market, self.name, timeframe,
                entry_price, sl, tp1, tp2, tp3, confidence=confidence_short
            )

        return None

    def check_exit(self, df: pd.DataFrame, signal: Dict,
                   current_price: float) -> Optional[str]:
        """Check exit conditions for swing trading."""
        if signal["signal_type"] == "LONG":
            if current_price <= signal["stop_loss"]:
                return "SL_HIT"
            for i, tp_key in enumerate(["take_profit_1", "take_profit_2", "take_profit_3"], 1):
                tp = signal.get(tp_key)
                if tp and current_price >= tp:
                    return f"TP{i}_HIT"
        else:
            if current_price >= signal["stop_loss"]:
                return "SL_HIT"
            for i, tp_key in enumerate(["take_profit_1", "take_profit_2", "take_profit_3"], 1):
                tp = signal.get(tp_key)
                if tp and current_price <= tp:
                    return f"TP{i}_HIT"

        trailing = abs(signal["entry_price"] - signal["stop_loss"]) * 0.02
        if signal["signal_type"] == "LONG" and current_price > signal["entry_price"]:
            new_sl = current_price - trailing
            if new_sl > signal["stop_loss"]:
                signal["stop_loss"] = new_sl
        elif signal["signal_type"] == "SHORT" and current_price < signal["entry_price"]:
            new_sl = current_price + trailing
            if new_sl < signal["stop_loss"]:
                signal["stop_loss"] = new_sl

        return None
