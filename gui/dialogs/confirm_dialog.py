"""Confirmation dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from config.constants import COLORS


class ConfirmDialog(QDialog):
    """Confirmation dialog for actions."""

    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 150)
        self.setModal(True)
        self.result = False
        self._setup_ui(message)

    def _setup_ui(self, message: str):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        no_btn = QPushButton("Xeyr")
        no_btn.clicked.connect(self._on_no)
        btn_layout.addWidget(no_btn)

        yes_btn = QPushButton("Bəli")
        yes_btn.setObjectName("primary")
        yes_btn.clicked.connect(self._on_yes)
        btn_layout.addWidget(yes_btn)

        layout.addLayout(btn_layout)

    def _on_yes(self):
        self.result = True
        self.accept()

    def _on_no(self):
        self.result = False
        self.reject()
