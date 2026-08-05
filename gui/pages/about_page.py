"""About page with application information."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from config.constants import APP_NAME, APP_VERSION, APP_AUTHOR, COLORS


class AboutPage(QWidget):
    """About page showing application information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the about page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(16)

        layout.addStretch()

        app_name = QLabel(APP_NAME)
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {COLORS['primary']};")
        layout.addWidget(app_name)

        version = QLabel(f"Versiya {APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"font-size: 16px; color: {COLORS['text_secondary']};")
        layout.addWidget(version)

        layout.addSpacing(20)

        desc = QLabel(
            "Universal Trading Siqnal Sistemi\n\n"
            "Kripto, Forex və Səhmlər bazarları üçün\n"
            "avtomatik siqnal generasiya sistemi.\n\n"
            "4 strategiya: Scalping, Day Trading, Swing, Trend Following\n"
            "Telegram bildirişləri\n"
            "Avtomatik trade funksiyası\n"
            "Backtest sistemi"
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; line-height: 1.5;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(20)

        author = QLabel(f"Tərtibatçı: {APP_AUTHOR}")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']};")
        layout.addWidget(author)

        license_label = QLabel("Lisenziya: MIT License")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        layout.addWidget(license_label)

        layout.addStretch()
