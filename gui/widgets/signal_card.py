"""Signal card widget for displaying trading signals."""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from config.constants import COLORS
from utils.helpers import format_price, get_signal_color, get_status_color


class SignalCard(QFrame):
    """Card widget for displaying a single signal."""

    close_clicked = pyqtSignal(int)
    detail_clicked = pyqtSignal(int)

    def __init__(self, signal_data: dict, parent=None):
        super().__init__(parent)
        self.signal_data = signal_data
        self.signal_id = signal_data.get("id", 0)
        self.setObjectName("card")
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Header
        header_layout = QHBoxLayout()
        sig_type = self.signal_data.get("signal_type", "LONG")
        emoji = "🟢" if sig_type == "LONG" else "🔴"
        color = get_signal_color(sig_type)

        type_label = QLabel(f"{emoji} {sig_type} {self.signal_data.get('symbol', '')}")
        type_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")

        confidence = self.signal_data.get("confidence", "MEDIUM")
        conf_color = COLORS["profit"] if confidence == "HIGH" else COLORS["warning"] if confidence == "MEDIUM" else COLORS["loss"]
        conf_label = QLabel(confidence)
        conf_label.setStyleSheet(f"color: {conf_color}; font-weight: bold; padding: 2px 8px; border-radius: 4px; background: {conf_color}22;")

        header_layout.addWidget(type_label)
        header_layout.addStretch()
        header_layout.addWidget(conf_label)
        layout.addLayout(header_layout)

        # Info rows
        info_items = [
            ("Bazar:", self.signal_data.get("market", "")),
            ("Strategiya:", self.signal_data.get("strategy", "")),
            ("Timeframe:", self.signal_data.get("timeframe", "")),
        ]
        for label, value in info_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("secondary")
            val = QLabel(str(value))
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            layout.addLayout(row)

        layout.addWidget(self._separator())

        # Price info
        prices = [
            ("Giriş:", format_price(self.signal_data.get("entry_price"))),
            ("Stop Loss:", format_price(self.signal_data.get("stop_loss"))),
            ("TP1:", format_price(self.signal_data.get("take_profit_1"))),
            ("TP2:", format_price(self.signal_data.get("take_profit_2"))),
            ("TP3:", format_price(self.signal_data.get("take_profit_3"))),
            ("R:R:", f"1:{self.signal_data.get('risk_reward_ratio', 0):.1f}"),
        ]
        for label, value in prices:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setObjectName("secondary")
            val = QLabel(value)
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            layout.addLayout(row)

        layout.addWidget(self._separator())

        # Status and time
        status = self.signal_data.get("status", "ACTIVE")
        status_color = get_status_color(status)
        status_row = QHBoxLayout()
        status_lbl = QLabel("Status:")
        status_lbl.setObjectName("secondary")
        status_val = QLabel(status)
        status_val.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        status_row.addWidget(status_lbl)
        status_row.addWidget(status_val)
        status_row.addStretch()
        layout.addLayout(status_row)

        time_row = QHBoxLayout()
        time_lbl = QLabel("Vaxt:")
        time_lbl.setObjectName("secondary")
        time_val = QLabel(str(self.signal_data.get("entry_time", ""))[:16])
        time_row.addWidget(time_lbl)
        time_row.addWidget(time_val)
        time_row.addStretch()
        layout.addLayout(time_row)

        # Buttons
        btn_layout = QHBoxLayout()
        if status == "ACTIVE":
            close_btn = QPushButton("Manual Bağla")
            close_btn.setObjectName("danger")
            close_btn.setFixedHeight(30)
            close_btn.clicked.connect(lambda: self.close_clicked.emit(self.signal_id))
            btn_layout.addWidget(close_btn)

        detail_btn = QPushButton("Detayl")
        detail_btn.setFixedHeight(30)
        detail_btn.clicked.connect(lambda: self.detail_clicked.emit(self.signal_id))
        btn_layout.addWidget(detail_btn)
        layout.addLayout(btn_layout)

    def _separator(self):
        """Create a separator line."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        return line

    def update_signal(self, signal_data: dict):
        """Update the card with new signal data."""
        self.signal_data = signal_data
        # Clear and rebuild
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    child2 = child.layout().takeAt(0)
                    if child2.widget():
                        child2.widget().deleteLater()
        self._setup_ui()
