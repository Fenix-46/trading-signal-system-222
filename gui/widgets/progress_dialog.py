"""Progress dialog for long-running operations."""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from config.constants import COLORS


class ProgressDialog(QDialog):
    """Progress dialog for backtest and other operations."""

    def __init__(self, title: str = "Əməliyyat davam edir...", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 120)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.status_label = QLabel("Zəhmət olmasa gözləyin...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setObjectName("secondary")
        layout.addWidget(self.detail_label)

    def set_progress(self, value: int, text: str = ""):
        """Update progress bar."""
        self.progress_bar.setValue(value)
        if text:
            self.detail_label.setText(text)

    def set_status(self, text: str):
        """Update status text."""
        self.status_label.setText(text)

    def set_range(self, min_val: int, max_val: int):
        """Set progress bar range."""
        self.progress_bar.setRange(min_val, max_val)
