"""Signal detail dialog for viewing signal information."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt
from config.constants import COLORS
from utils.helpers import format_price, format_percent, get_signal_color, get_status_color


class SignalDetailDialog(QDialog):
    """Dialog showing detailed signal information."""

    def __init__(self, signal, parent=None):
        super().__init__(parent)
        self.signal = signal
        self.setWindowTitle(f"Siqnal Detalı - {signal.symbol}")
        self.setMinimumSize(450, 550)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Header
        sig_type = self.signal.signal_type or "LONG"
        emoji = "🟢" if sig_type == "LONG" else "🔴"
        color = get_signal_color(sig_type)

        header = QLabel(f"{emoji} {sig_type} {self.signal.symbol}")
        header.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
        layout.addWidget(header)

        layout.addWidget(self._separator())

        # Info section
        info_items = [
            ("Bazar:", self.signal.market or ""),
            ("Strategiya:", self.signal.strategy or ""),
            ("Timeframe:", self.signal.timeframe or ""),
            ("Confidence:", self.signal.confidence or "MEDIUM"),
            ("Status:", self.signal.status or "ACTIVE"),
            ("Vaxt:", str(self.signal.entry_time or "")[:19]),
        ]
        for label, value in info_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("secondary")
            lbl.setFixedWidth(100)
            val = QLabel(str(value))
            if label == "Status:":
                status_color = get_status_color(value)
                val.setStyleSheet(f"color: {status_color}; font-weight: bold;")
            if label == "Confidence:":
                conf_color = COLORS["profit"] if value == "HIGH" else COLORS["warning"] if value == "MEDIUM" else COLORS["loss"]
                val.setStyleSheet(f"color: {conf_color}; font-weight: bold;")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            layout.addLayout(row)

        layout.addWidget(self._separator())

        # Price section
        price_items = [
            ("Giriş Qiyməti:", format_price(self.signal.entry_price)),
            ("Stop Loss:", format_price(self.signal.stop_loss)),
            ("Take Profit 1:", format_price(self.signal.take_profit_1)),
            ("Take Profit 2:", format_price(self.signal.take_profit_2)),
            ("Take Profit 3:", format_price(self.signal.take_profit_3)),
        ]
        for label, value in price_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("secondary")
            lbl.setFixedWidth(120)
            val = QLabel(value)
            if "Loss" in label:
                val.setStyleSheet(f"color: {COLORS['loss']};")
            elif "Profit" in label:
                val.setStyleSheet(f"color: {COLORS['profit']};")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            layout.addLayout(row)

        layout.addWidget(self._separator())

        # Risk/Reward
        rr = self.signal.risk_reward_ratio or 0
        rr_label = QLabel(f"Risk/Reward: 1:{rr:.1f}")
        rr_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['primary']};")
        layout.addWidget(rr_label)

        # PnL if exists
        if self.signal.pnl_percent is not None:
            pnl_color = COLORS["profit"] if self.signal.pnl_percent >= 0 else COLORS["loss"]
            pnl_label = QLabel(f"PnL: {format_percent(self.signal.pnl_percent)}")
            pnl_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {pnl_color};")
            layout.addWidget(pnl_label)

        # Notes
        if self.signal.notes:
            notes_label = QLabel(f"Qeydlər: {self.signal.notes}")
            notes_label.setObjectName("secondary")
            notes_label.setWordWrap(True)
            layout.addWidget(notes_label)

        layout.addStretch()

        # Close button
        close_btn = QPushButton("Bağla")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _separator(self):
        """Create a separator line."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        return line
