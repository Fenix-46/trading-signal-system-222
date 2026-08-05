"""Filter bar widget for signals page."""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame
)
from PyQt6.QtCore import pyqtSignal
from config.constants import COLORS


class FilterBar(QWidget):
    """Filter toolbar for signals."""

    filter_changed = pyqtSignal()
    refresh_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedHeight(50)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the filter bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # Market filter
        market_label = QLabel("Bazar:")
        market_label.setObjectName("secondary")
        self.market_combo = QComboBox()
        self.market_combo.addItems(["Hamısı", "Kripto", "Forex", "Səhmlər"])
        self.market_combo.currentIndexChanged.connect(self.filter_changed.emit)
        self.market_combo.setFixedWidth(120)

        # Strategy filter
        strategy_label = QLabel("Strategiya:")
        strategy_label.setObjectName("secondary")
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Hamısı", "Scalping", "Day Trading", "Swing", "Trend Following"])
        self.strategy_combo.currentIndexChanged.connect(self.filter_changed.emit)
        self.strategy_combo.setFixedWidth(140)

        # Status filter
        status_label = QLabel("Status:")
        status_label.setObjectName("secondary")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Hamısı", "Active", "Closed", "SL Hit", "TP Hit"])
        self.status_combo.currentIndexChanged.connect(self.filter_changed.emit)
        self.status_combo.setFixedWidth(120)

        # Refresh button
        refresh_btn = QPushButton("Yenilə")
        refresh_btn.setObjectName("primary")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self.refresh_clicked.emit)

        layout.addWidget(market_label)
        layout.addWidget(self.market_combo)
        layout.addWidget(self._separator())
        layout.addWidget(strategy_label)
        layout.addWidget(self.strategy_combo)
        layout.addWidget(self._separator())
        layout.addWidget(status_label)
        layout.addWidget(self.status_combo)
        layout.addStretch()
        layout.addWidget(refresh_btn)

    def _separator(self):
        """Create a vertical separator."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet(f"background-color: {COLORS['border']}; max-width: 1px;")
        return line

    def get_filters(self) -> dict:
        """Get current filter values."""
        market_map = {"Hamısı": "all", "Kripto": "crypto", "Forex": "forex", "Səhmlər": "stocks"}
        strategy_map = {"Hamısı": "all", "Scalping": "scalping", "Day Trading": "day_trading",
                       "Swing": "swing", "Trend Following": "trend_following"}
        status_map = {"Hamısı": "all", "Active": "ACTIVE", "Closed": "CLOSED",
                     "SL Hit": "SL_HIT", "TP Hit": "TP1_HIT"}
        return {
            "market": market_map.get(self.market_combo.currentText(), "all"),
            "strategy": strategy_map.get(self.strategy_combo.currentText(), "all"),
            "status": status_map.get(self.status_combo.currentText(), "all"),
        }
