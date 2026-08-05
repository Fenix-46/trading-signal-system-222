"""Signal engine - generates trading signals based on strategies."""

import logging
from datetime import datetime
from typing import Optional, Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


class SignalEngine:
    """Main signal generation engine."""

    def __init__(self):
        self._strategies = {}
        self._register_strategies()

    def _register_strategies(self):
        """Register all available strategies."""
        from strategies.scalping_strategy import ScalpingStrategy
        from strategies.day_trading_strategy import DayTradingStrategy
        from strategies.swing_trading_strategy import SwingTradingStrategy
        from strategies.trend_following_strategy import TrendFollowingStrategy
        self._strategies = {
            "scalping": ScalpingStrategy(),
            "day_trading": DayTradingStrategy(),
            "swing": SwingTradingStrategy(),
            "trend_following": TrendFollowingStrategy(),
        }

    def generate_signal(self, df: pd.DataFrame, strategy_name: str,
                        symbol: str, market: str, timeframe: str) -> Optional[Dict]:
        """Generate a trading signal for the given data and strategy."""
        if df is None or df.empty:
            return None
        strategy = self._strategies.get(strategy_name)
        if strategy is None:
            logger.warning(f"Unknown strategy: {strategy_name}")
            return None
        try:
            signal = strategy.analyze(df, symbol, market, timeframe)
            if signal is not None:
                signal["created_at"] = datetime.utcnow().isoformat()
                logger.info(f"Signal generated: {signal['signal_type']} {symbol} ({strategy_name})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol} ({strategy_name}): {e}")
            return None

    def check_exit_conditions(self, df: pd.DataFrame, signal: Dict,
                              current_price: float) -> Optional[str]:
        """Check if exit conditions are met for an open signal."""
        if df is None or df.empty:
            return None
        try:
            strategy_name = signal.get("strategy", "")
            strategy = self._strategies.get(strategy_name)
            if strategy is None:
                return None
            return strategy.check_exit(df, signal, current_price)
        except Exception as e:
            logger.error(f"Error checking exit conditions: {e}")
            return None

    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names."""
        return list(self._strategies.keys())
