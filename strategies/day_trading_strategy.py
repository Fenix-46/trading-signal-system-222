"""Day trading strategy implementation."""

from typing import Optional, Dict
import pandas as pd
import logging
from strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class DayTradingStrategy(BaseStrategy):
    """Day trading strategy for intraday trades."""

    def __init__(self):
        super().__init__()
        self.name = "day_trading"
        self.display_name = "Day Trading"

    def analyze(self, df: pd.DataFrame, symbol: str, market: str,
                timeframe: str) -> Optional[Dict]:
        """Analyze for day trading signals."""
        if len(df) < 50:
            return None
        last = df.iloc[-1]
        prev = df.iloc[-2]

        long_conditions = 0
        short_conditions = 0
        total_conditions = 7

        # EMA trend
        if last.get("ema_20", 0) > last.get("ema_50", 0):
            long_conditions += 1
        if last.get("ema_20", 0) < last.get("ema_50", 0):
            short_conditions += 1

        # RSI trend
        rsi = last.get("rsi", 50)
        if rsi > 50:
            long_conditions += 1
        if rsi < 50:
            short_conditions += 1

        # MACD crossover
        if prev.get("macd", 0) < prev.get("macd_signal", 0) and last.get("macd", 0) > last.get("macd_signal", 0):
            long_conditions += 1
        if prev.get("macd", 0) > prev.get("macd_signal", 0) and last.get("macd", 0) < last.get("macd_signal", 0):
            short_conditions += 1

        # ADX strong trend
        adx = last.get("adx", 0)
        if adx > 25:
            long_conditions += 1
            short_conditions += 1

        # Volume increasing
        if last.get("volume_ratio", 1) > 1.0:
            long_conditions += 1
            short_conditions += 1

        # Price near EMA 20 (pullback)
        ema20 = last.get("ema_20", 0)
        price = last.get("close", 0)
        if ema20 > 0:
            distance_pct = abs(price - ema20) / ema20 * 100
            if distance_pct < 0.5:
                if price > ema20:
                    long_conditions += 1
                else:
                    short_conditions += 1

        # ATR normal range
        atr = last.get("atr", 0)
        if atr > 0 and price > 0:
            atr_pct = atr / price * 100
            if 0.2 < atr_pct < 3.0:
                long_conditions += 1
                short_conditions += 1

        confidence_long = self._calculate_confidence(long_conditions, total_conditions)
        confidence_short = self._calculate_confidence(short_conditions, total_conditions)

        entry_price = price

        if confidence_long and long_conditions >= 5:
            sl = self._find_swing_low(df, 20)
            if sl >= entry_price:
                sl = entry_price - atr * 2
            risk = entry_price - sl
            tp1 = entry_price + risk * 1.5
            tp2 = entry_price + risk * 2
            tp3 = entry_price + risk * 3
            return self._create_signal(
                "LONG", symbol, market, self.name, timeframe,
                entry_price, sl, tp1, tp2, tp3, confidence=confidence_long
            )

        if confidence_short and short_conditions >= 5:
            sl = self._find_swing_high(df, 20)
            if sl <= entry_price:
                sl = entry_price + atr * 2
            risk = sl - entry_price
            tp1 = entry_price - risk * 1.5
            tp2 = entry_price - risk * 2
            tp3 = entry_price - risk * 3
            return self._create_signal(
                "SHORT", symbol, market, self.name, timeframe,
                entry_price, sl, tp1, tp2, tp3, confidence=confidence_short
            )

        return None

    def check_exit(self, df: pd.DataFrame, signal: Dict,
                   current_price: float) -> Optional[str]:
        """Check exit conditions for day trading."""
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

        trailing = abs(signal["entry_price"] - signal["stop_loss"]) * 0.01
        if signal["signal_type"] == "LONG" and current_price > signal["entry_price"]:
            new_sl = current_price - trailing
            if new_sl > signal["stop_loss"]:
                signal["stop_loss"] = new_sl
        elif signal["signal_type"] == "SHORT" and current_price < signal["entry_price"]:
            new_sl = current_price + trailing
            if new_sl < signal["stop_loss"]:
                signal["stop_loss"] = new_sl

        return None
