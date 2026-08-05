"""Trade executor for automated trading simulation."""

import logging
from datetime import datetime
from typing import Optional, Dict
from sqlalchemy.orm import Session
from database.models import Trade, Signal
from config.constants import TRADE_STATUSES

logger = logging.getLogger(__name__)


class TradeExecutor:
    """Handles trade execution (simulation)."""

    def __init__(self, session: Session):
        self.session = session
        self.default_balance = 10000.0

    def open_trade(self, signal: Dict, quantity: float, is_auto: bool = True) -> Optional[Trade]:
        """Open a new trade based on a signal."""
        try:
            side = "BUY" if signal["signal_type"] == "LONG" else "SELL"
            trade = Trade(
                signal_id=signal.get("id"),
                symbol=signal["symbol"],
                side=side,
                entry_price=signal["entry_price"],
                quantity=quantity,
                status=TRADE_STATUSES["OPEN"],
                is_auto=1 if is_auto else 0,
                opened_at=datetime.utcnow().isoformat()
            )
            self.session.add(trade)
            self.session.commit()
            logger.info(f"Trade opened: {side} {signal['symbol']} @ {signal['entry_price']}")
            return trade
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error opening trade: {e}")
            return None

    def close_trade(self, trade_id: int, exit_price: float, pnl: float,
                    pnl_percent: float) -> Optional[Trade]:
        """Close an open trade."""
        try:
            trade = self.session.query(Trade).filter(Trade.id == trade_id).first()
            if not trade:
                return None
            trade.exit_price = exit_price
            trade.pnl = pnl
            trade.pnl_percent = pnl_percent
            trade.status = TRADE_STATUSES["CLOSED"]
            trade.closed_at = datetime.utcnow().isoformat()
            self.session.commit()
            logger.info(f"Trade closed: {trade.symbol} PnL: {pnl_percent:.2f}%")
            return trade
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error closing trade: {e}")
            return None

    def calculate_pnl(self, trade: Trade, current_price: float):
        """Calculate PnL for a trade."""
        if trade.side == "BUY":
            pnl = (current_price - trade.entry_price) * trade.quantity
            pnl_percent = ((current_price - trade.entry_price) / trade.entry_price) * 100
        else:
            pnl = (trade.entry_price - current_price) * trade.quantity
            pnl_percent = ((trade.entry_price - current_price) / trade.entry_price) * 100
        return round(pnl, 2), round(pnl_percent, 4)
