"""Base strategy abstract class."""

from abc import ABC, abstractmethod
from typing import Optional, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""

    def __init__(self):
        self.name = "base"
        self.display_name = "Base Strategy"

    @abstractmethod
    def analyze(self, df: pd.DataFrame, symbol: str, market: str,
                timeframe: str) -> Optional[Dict]:
        """Analyze market data and generate a signal if conditions are met."""
        pass

    @abstractmethod
    def check_exit(self, df: pd.DataFrame, signal: Dict,
                   current_price: float) -> Optional[str]:
        """Check if exit conditions are met."""
        pass

    def _calculate_confidence(self, conditions_met: int, total_conditions: int) -> str:
        """Calculate confidence level based on conditions met."""
        if total_conditions == 0:
            return "LOW"
        ratio = conditions_met / total_conditions
        if ratio >= 0.80:
            return "HIGH"
        elif ratio >= 0.60:
            return "MEDIUM"
        elif ratio >= 0.40:
            return "LOW"
        return None

    def _find_swing_low(self, df: pd.DataFrame, lookback: int = 10) -> float:
        """Find the swing low price."""
        recent = df.tail(lookback)
        return recent["low"].min()

    def _find_swing_high(self, df: pd.DataFrame, lookback: int = 10) -> float:
        """Find the swing high price."""
        recent = df.tail(lookback)
        return recent["high"].max()

    def _create_signal(self, signal_type: str, symbol: str, market: str,
                       strategy: str, timeframe: str, entry_price: float,
                       stop_loss: float, take_profit_1: float,
                       take_profit_2: float = None, take_profit_3: float = None,
                       confidence: str = "MEDIUM") -> Dict:
        """Create a signal dictionary."""
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit_1 - entry_price) if take_profit_1 else risk
        rr_ratio = round(reward / risk, 2) if risk > 0 else 1.0

        return {
            "symbol": symbol,
            "market": market,
            "strategy": strategy,
            "signal_type": signal_type,
            "entry_price": round(entry_price, 8),
            "stop_loss": round(stop_loss, 8),
            "take_profit_1": round(take_profit_1, 8) if take_profit_1 else None,
            "take_profit_2": round(take_profit_2, 8) if take_profit_2 else None,
            "take_profit_3": round(take_profit_3, 8) if take_profit_3 else None,
            "risk_reward_ratio": rr_ratio,
            "confidence": confidence,
            "timeframe": timeframe,
        }
