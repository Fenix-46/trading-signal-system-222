"""Risk management module."""

import logging
from datetime import datetime, date
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from database.models import Signal, Trade, UserSettings
from config.constants import SIGNAL_STATUSES, TRADE_STATUSES

logger = logging.getLogger(__name__)


class RiskManager:
    """Manages trading risk and position sizing."""

    def __init__(self, session: Session):
        self.session = session

    def calculate_position_size(self, balance: float, risk_percent: float,
                                entry_price: float, stop_loss: float) -> float:
        """Calculate position size based on risk parameters."""
        risk_amount = balance * (risk_percent / 100)
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit == 0:
            return 0.0
        position_size = risk_amount / risk_per_unit
        return round(position_size, 8)

    def can_open_position(self, symbol: str, signal_type: str) -> bool:
        """Check if a new position can be opened."""
        settings = self.session.query(UserSettings).first()
        if not settings:
            return False

        # Check max open positions
        open_trades = self.session.query(Trade).filter(
            Trade.status == TRADE_STATUSES["OPEN"]
        ).count()
        if open_trades >= settings.max_open_positions:
            logger.warning(f"Max open positions ({settings.max_open_positions}) reached.")
            return False

        # Check same symbol same direction
        existing = self.session.query(Trade).filter(
            Trade.symbol == symbol,
            Trade.status == TRADE_STATUSES["OPEN"],
            Trade.side == ("BUY" if signal_type == "LONG" else "SELL")
        ).first()
        if existing:
            logger.warning(f"Already have open position for {symbol} {signal_type}.")
            return False

        return True

    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been reached."""
        settings = self.session.query(UserSettings).first()
        if not settings:
            return True

        today = date.today().isoformat()
        today_trades = self.session.query(Trade).filter(
            Trade.status == TRADE_STATUSES["CLOSED"],
            Trade.closed_at.like(f"{today}%")
        ).all()

        daily_pnl = sum(t.pnl_percent or 0 for t in today_trades)
        if daily_pnl <= -settings.daily_loss_limit:
            logger.warning(f"Daily loss limit ({settings.daily_loss_limit}%) reached. PnL: {daily_pnl}%")
            return False
        return True

    def get_daily_pnl(self) -> float:
        """Get today's total PnL percentage."""
        today = date.today().isoformat()
        today_trades = self.session.query(Trade).filter(
            Trade.status == TRADE_STATUSES["CLOSED"],
            Trade.closed_at.like(f"{today}%")
        ).all()
        return sum(t.pnl_percent or 0 for t in today_trades)

    def get_open_positions_count(self) -> int:
        """Get count of open positions."""
        return self.session.query(Trade).filter(
            Trade.status == TRADE_STATUSES["OPEN"]
        ).count()

    def get_active_signals_count(self) -> int:
        """Get count of active signals."""
        return self.session.query(Signal).filter(
            Signal.status == SIGNAL_STATUSES["ACTIVE"]
        ).count()

    def validate_signal(self, signal_data: Dict) -> bool:
        """Validate a signal before creation."""
        required_fields = ["symbol", "market", "strategy", "signal_type",
                          "entry_price", "stop_loss"]
        for field in required_fields:
            if field not in signal_data or signal_data[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False

        if signal_data["signal_type"] not in ["LONG", "SHORT"]:
            logger.warning(f"Invalid signal type: {signal_data['signal_type']}")
            return False

        entry = signal_data["entry_price"]
        sl = signal_data["stop_loss"]
        if signal_data["signal_type"] == "LONG" and sl >= entry:
            logger.warning("LONG signal: SL must be below entry.")
            return False
        if signal_data["signal_type"] == "SHORT" and sl <= entry:
            logger.warning("SHORT signal: SL must be above entry.")
            return False

        return True
