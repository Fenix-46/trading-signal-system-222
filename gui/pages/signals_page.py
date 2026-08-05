"""Signals page showing all signals as cards."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session
from database.models import Signal
from database.db_manager import DatabaseManager
from gui.widgets.filter_bar import FilterBar
from gui.widgets.signal_card import SignalCard
from gui.dialogs.signal_detail_dialog import SignalDetailDialog
from config.constants import COLORS


class SignalsPage(QWidget):
    """Signals page with filter and signal cards."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signal_cards = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the signals page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Siqnallar")
        title.setObjectName("title")
        layout.addWidget(title)

        self.filter_bar = FilterBar()
        self.filter_bar.filter_changed.connect(self.refresh)
        self.filter_bar.refresh_clicked.connect(self.refresh)
        layout.addWidget(self.filter_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout(self.cards_widget)
        self.cards_layout.setSpacing(12)
        self.scroll_area.setWidget(self.cards_widget)
        layout.addWidget(self.scroll_area)

    def refresh(self):
        """Refresh signals display."""
        try:
            db = DatabaseManager()
            session = db.get_session()

            filters = self.filter_bar.get_filters()
            query = session.query(Signal)

            if filters["market"] != "all":
                query = query.filter(Signal.market == filters["market"])
            if filters["strategy"] != "all":
                query = query.filter(Signal.strategy == filters["strategy"])
            if filters["status"] != "all":
                query = query.filter(Signal.status == filters["status"])

            signals = query.order_by(Signal.created_at.desc()).limit(50).all()

            # Clear existing cards
            for card in self.signal_cards:
                card.setParent(None)
                card.deleteLater()
            self.signal_cards.clear()

            # Add new cards
            cols = max(1, (self.scroll_area.width() - 40) // 320)
            for i, signal in enumerate(signals):
                signal_data = {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "market": signal.market,
                    "strategy": signal.strategy,
                    "signal_type": signal.signal_type,
                    "entry_price": signal.entry_price,
                    "stop_loss": signal.stop_loss,
                    "take_profit_1": signal.take_profit_1,
                    "take_profit_2": signal.take_profit_2,
                    "take_profit_3": signal.take_profit_3,
                    "risk_reward_ratio": signal.risk_reward_ratio,
                    "confidence": signal.confidence,
                    "timeframe": signal.timeframe,
                    "status": signal.status,
                    "pnl_percent": signal.pnl_percent,
                    "entry_time": signal.entry_time,
                }
                card = SignalCard(signal_data)
                card.detail_clicked.connect(self._show_detail)
                self.signal_cards.append(card)
                row = i // cols
                col = i % cols
                self.cards_layout.addWidget(card, row, col)

            session.close()
        except Exception as e:
            print(f"Signals refresh error: {e}")

    def _show_detail(self, signal_id: int):
        """Show signal detail dialog."""
        try:
            db = DatabaseManager()
            session = db.get_session()
            signal = session.query(Signal).filter(Signal.id == signal_id).first()
            if signal:
                dialog = SignalDetailDialog(signal, self)
                dialog.exec()
            session.close()
        except Exception as e:
            print(f"Error showing signal detail: {e}")
