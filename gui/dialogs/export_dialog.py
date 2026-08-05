"""Export dialog for CSV export options."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt


class ExportDialog(QDialog):
    """Export dialog for CSV export."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export CSV")
        self.setFixedSize(350, 250)
        self.setModal(True)
        self.export_path = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel("CSV Export")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.all_check = QCheckBox("Bütün siqnallar")
        self.all_check.setChecked(True)
        layout.addWidget(self.all_check)

        self.active_check = QCheckBox("Yalnız aktiv siqnallar")
        layout.addWidget(self.active_check)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("Ləğv et")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        export_btn = QPushButton("Export et")
        export_btn.setObjectName("primary")
        export_btn.clicked.connect(self._export)
        btn_layout.addWidget(export_btn)

        layout.addLayout(btn_layout)

    def _export(self):
        """Handle export button click."""
        path, _ = QFileDialog.getSaveFileName(
            self, "CSV Saxla", "signals.csv", "CSV Files (*.csv)"
        )
        if path:
            self.export_path = path
            self.accept()
