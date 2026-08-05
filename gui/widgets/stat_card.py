"""Stat card widget for dashboard and statistics."""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from config.constants import COLORS


class StatCard(QFrame):
    """A card displaying a single statistic."""

    def __init__(self, title: str, value: str = "0", color: str = None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFixedHeight(100)
        self.setMinimumWidth(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("stat-label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.title_label)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat-value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.value_label)

        layout.addStretch()

    def set_value(self, value: str, color: str = None):
        """Update the displayed value."""
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")

    def set_title(self, title: str):
        """Update the title."""
        self.title_label.setText(title)
