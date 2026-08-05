"""System tray icon manager."""

import logging
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt6.QtCore import pyqtSignal, QObject
from config.constants import COLORS

logger = logging.getLogger(__name__)


class SystemTrayManager(QObject):
    """Manages system tray icon and menu."""

    open_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()
    exit_clicked = pyqtSignal()
    toggle_auto_trade = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None
        self.auto_trade_enabled = False
        self._setup_tray()

    def _setup_tray(self):
        """Setup system tray icon."""
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self._create_icon(COLORS["primary"]))
        self.tray_icon.setToolTip("Trading Signal System - Active")

        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #16213e;
                color: white;
                border: 1px solid #1e3a5f;
            }
            QMenu::item:selected {
                background-color: #00d4ff;
                color: #1a1a2e;
            }
        """)

        open_action = menu.addAction(" Aç")
        open_action.triggered.connect(self.open_clicked.emit)

        menu.addSeparator()

        self.auto_trade_action = menu.addAction(" Auto Trade: OFF")
        self.auto_trade_action.triggered.connect(self._toggle_auto_trade)

        settings_action = menu.addAction(" Parametrlər")
        settings_action.triggered.connect(self.settings_clicked.emit)

        menu.addSeparator()

        exit_action = menu.addAction(" Çıxış")
        exit_action.triggered.connect(self.exit_clicked.emit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._on_activated)

    def _create_icon(self, color: str) -> QIcon:
        """Create a simple colored icon."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(QColor(color))
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        return QIcon(pixmap)

    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.open_clicked.emit()

    def _toggle_auto_trade(self):
        """Toggle auto trade."""
        self.auto_trade_enabled = not self.auto_trade_enabled
        status = "ON" if self.auto_trade_enabled else "OFF"
        self.auto_trade_action.setText(f" Auto Trade: {status}")
        self.toggle_auto_trade.emit(self.auto_trade_enabled)

    def show(self):
        """Show tray icon."""
        self.tray_icon.show()

    def hide(self):
        """Hide tray icon."""
        self.tray_icon.hide()

    def show_notification(self, title: str, message: str):
        """Show balloon notification."""
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 5000)

    def set_active(self, has_active_signals: bool):
        """Update icon based on active signals."""
        if has_active_signals:
            self.tray_icon.setIcon(self._create_icon(COLORS["profit"]))
            self.tray_icon.setToolTip("Trading Signal System - Active Signals")
        else:
            self.tray_icon.setIcon(self._create_icon(COLORS["primary"]))
            self.tray_icon.setToolTip("Trading Signal System - Active")
