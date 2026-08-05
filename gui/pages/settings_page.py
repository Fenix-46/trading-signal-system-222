"""Settings page for application configuration."""

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QCheckBox, QScrollArea, QFrame,
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from sqlalchemy.orm import Session
from database.models import User, UserSettings
from database.db_manager import DatabaseManager
from gui.widgets.toggle_switch import ToggleSwitch
from gui.widgets.risk_slider import RiskSlider
from config.constants import COLORS, TIMEFRAMES
from core.notification_manager import NotificationManager


class SettingsPage(QWidget):
    """Settings page for all application settings."""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.toggles = {}
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Setup the settings page UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(16)

        title = QLabel("Parametrlər")
        title.setObjectName("title")
        layout.addWidget(title)

        # General Settings
        general_card = self._create_section("Ümumi")
        general_layout = general_card.layout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        general_layout.addLayout(self._form_row("Tema:", self.theme_combo))

        self.minimize_tray_toggle = ToggleSwitch(True)
        general_layout.addLayout(self._form_row("Tray-da saxla:", self.minimize_tray_toggle))

        self.sound_toggle = ToggleSwitch(True)
        general_layout.addLayout(self._form_row("Səs bildirişləri:", self.sound_toggle))

        layout.addWidget(general_card)

        # Market Settings
        market_card = self._create_section("Bazar")
        market_layout = market_card.layout()

        self.crypto_check = QCheckBox("Kripto")
        self.crypto_check.setChecked(True)
        market_layout.addWidget(self.crypto_check)

        self.forex_check = QCheckBox("Forex")
        self.forex_check.setChecked(True)
        market_layout.addWidget(self.forex_check)

        self.stocks_check = QCheckBox("Səhmlər")
        self.stocks_check.setChecked(True)
        market_layout.addWidget(self.stocks_check)

        layout.addWidget(market_card)

        # Strategy Settings
        strategy_card = self._create_section("Strategiya")
        strategy_layout = strategy_card.layout()

        self.scalping_check = QCheckBox("Scalping")
        self.scalping_check.setChecked(True)
        strategy_layout.addWidget(self.scalping_check)

        self.daytrading_check = QCheckBox("Day Trading")
        self.daytrading_check.setChecked(True)
        strategy_layout.addWidget(self.daytrading_check)

        self.swing_check = QCheckBox("Swing Trading")
        self.swing_check.setChecked(True)
        strategy_layout.addWidget(self.swing_check)

        self.trend_check = QCheckBox("Trend Following")
        self.trend_check.setChecked(True)
        strategy_layout.addWidget(self.trend_check)

        layout.addWidget(strategy_card)

        # Risk Settings
        risk_card = self._create_section("Risk İdarəetməsi")
        risk_layout = risk_card.layout()

        self.risk_slider = RiskSlider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.1)
        risk_layout.addWidget(self.risk_slider)

        self.max_positions_spin = QSpinBox()
        self.max_positions_spin.setRange(1, 10)
        self.max_positions_spin.setValue(3)
        risk_layout.addLayout(self._form_row("Maks Pozisiya:", self.max_positions_spin))

        self.daily_loss_slider = RiskSlider("Günlük Loss Limit (%)", 1.0, 10.0, 5.0, 0.5)
        risk_layout.addWidget(self.daily_loss_slider)

        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(TIMEFRAMES)
        self.timeframe_combo.setCurrentText("15m")
        risk_layout.addLayout(self._form_row("Timeframe:", self.timeframe_combo))

        layout.addWidget(risk_card)

        # Telegram Settings
        telegram_card = self._create_section("Telegram")
        telegram_layout = telegram_card.layout()

        self.bot_token_input = QLineEdit()
        self.bot_token_input.setPlaceholderText("Bot Token daxil edin...")
        telegram_layout.addLayout(self._form_row("Bot Token:", self.bot_token_input))

        self.chat_id_input = QLineEdit()
        self.chat_id_input.setPlaceholderText("Chat ID daxil edin...")
        telegram_layout.addLayout(self._form_row("Chat ID:", self.chat_id_input))

        self.telegram_toggle = ToggleSwitch(True)
        telegram_layout.addLayout(self._form_row("Bildirişlər:", self.telegram_toggle))

        test_btn = QPushButton("Test Bildiriş Göndər")
        test_btn.setObjectName("primary")
        test_btn.clicked.connect(self._test_telegram)
        telegram_layout.addWidget(test_btn)

        layout.addWidget(telegram_card)

        # Auto Trade Settings
        auto_card = self._create_section("Avtomatik Trade")
        auto_layout = auto_card.layout()

        self.auto_trade_toggle = ToggleSwitch(False)
        auto_layout.addLayout(self._form_row("Auto Trade:", self.auto_trade_toggle))

        warning = QLabel("⚠️ Avtomatik trade aktivdir. Risk idarəetmənizi yoxlayın.")
        warning.setStyleSheet(f"color: {COLORS['warning']}; font-size: 11px;")
        warning.setWordWrap(True)
        auto_layout.addWidget(warning)

        layout.addWidget(auto_card)

        # Data Management
        data_card = self._create_section("Məlumat İdarəetməsi")
        data_layout = data_card.layout()

        btn_row = QHBoxLayout()
        reset_btn = QPushButton("Datanı Sıfırla")
        reset_btn.setObjectName("danger")
        reset_btn.clicked.connect(self._reset_data)
        btn_row.addWidget(reset_btn)

        backup_btn = QPushButton("Database Backup")
        backup_btn.clicked.connect(self._backup_database)
        btn_row.addWidget(backup_btn)

        restore_btn = QPushButton("Database Restore")
        restore_btn.clicked.connect(self._restore_database)
        btn_row.addWidget(restore_btn)

        data_layout.addLayout(btn_row)
        layout.addWidget(data_card)

        # Save button
        save_btn = QPushButton("Parametrləri Saxla")
        save_btn.setObjectName("primary")
        save_btn.setFixedHeight(40)
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_section(self, title: str) -> QFrame:
        """Create a section card."""
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(8)
        label = QLabel(title)
        label.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {COLORS['primary']};")
        card_layout.addWidget(label)
        return card

    def _form_row(self, label: str, widget) -> QHBoxLayout:
        """Create a form row."""
        row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setFixedWidth(120)
        row.addWidget(lbl)
        row.addWidget(widget)
        row.addStretch()
        return row

    def _load_settings(self):
        """Load settings from database."""
        try:
            db = DatabaseManager()
            session = db.get_session()
            settings = session.query(UserSettings).first()
            user = session.query(User).first()

            if settings:
                self.risk_slider.set_value(settings.risk_per_trade)
                self.max_positions_spin.setValue(settings.max_open_positions)
                self.daily_loss_slider.set_value(settings.daily_loss_limit)
                self.timeframe_combo.setCurrentText(settings.timeframe)
                self.sound_toggle.set_state(bool(settings.sound_enabled))
                self.telegram_toggle.set_state(bool(settings.notifications_enabled))

            if user:
                self.bot_token_input.setText(user.telegram_bot_token or "")
                self.chat_id_input.setText(user.telegram_chat_id or "")
                self.auto_trade_toggle.set_state(bool(user.auto_trade_enabled))

            session.close()
        except Exception as e:
            print(f"Load settings error: {e}")

    def _save_settings(self):
        """Save settings to database."""
        try:
            db = DatabaseManager()
            session = db.get_session()

            settings = session.query(UserSettings).first()
            if settings:
                settings.risk_per_trade = self.risk_slider.get_value()
                settings.max_open_positions = self.max_positions_spin.value()
                settings.daily_loss_limit = self.daily_loss_slider.get_value()
                settings.timeframe = self.timeframe_combo.currentText()
                settings.sound_enabled = 1 if self.sound_toggle.is_on() else 0
                settings.notifications_enabled = 1 if self.telegram_toggle.is_on() else 0

            user = session.query(User).first()
            if user:
                user.telegram_bot_token = self.bot_token_input.text()
                user.telegram_chat_id = self.chat_id_input.text()
                user.auto_trade_enabled = 1 if self.auto_trade_toggle.is_on() else 0

            session.commit()
            session.close()
            self.settings_changed.emit()
            QMessageBox.information(self, "Uğurlu", "Parametrlər saxlanıldı!")
        except Exception as e:
            QMessageBox.critical(self, "Xəta", f"Parametrlər saxlanarkən xəta: {e}")

    def _test_telegram(self):
        """Send test Telegram notification."""
        token = self.bot_token_input.text()
        chat_id = self.chat_id_input.text()
        if not token or not chat_id:
            QMessageBox.warning(self, "Xəta", "Bot Token və Chat ID daxil edin!")
            return
        try:
            db = DatabaseManager()
            session = db.get_session()
            user = session.query(User).first()
            if user:
                user.telegram_bot_token = token
                user.telegram_chat_id = chat_id
                session.commit()
            notifier = NotificationManager(session)
            success = notifier.send_test_notification()
            session.close()
            if success:
                QMessageBox.information(self, "Uğurlu", "Test bildirişi göndərildi!")
            else:
                QMessageBox.warning(self, "Xəta", "Bildiriş göndərilə bilmədi. Token və Chat ID-ni yoxlayın.")
        except Exception as e:
            QMessageBox.critical(self, "Xəta", f"Test bildirişi xətası: {e}")

    def _reset_data(self):
        """Reset all data."""
        reply = QMessageBox.question(
            self, "Təsdiq", "Bütün məlumatlar silinəcək. Davam edilsin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db = DatabaseManager()
                db.drop_tables()
                db.create_tables()
                from database.seed_data import seed_database
                seed_database()
                QMessageBox.information(self, "Uğurlu", "Məlumatlar sıfırlandı!")
            except Exception as e:
                QMessageBox.critical(self, "Xəta", f"Sıfırlama xətası: {e}")

    def _backup_database(self):
        """Backup database."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Database Backup", "trading_signals_backup.db", "Database (*.db)"
        )
        if path:
            try:
                db = DatabaseManager()
                if db.backup_database(path):
                    QMessageBox.information(self, "Uğurlu", f"Backup yaradıldı: {path}")
                else:
                    QMessageBox.warning(self, "Xəta", "Backup yaradıla bilmədi!")
            except Exception as e:
                QMessageBox.critical(self, "Xəta", f"Backup xətası: {e}")

    def _restore_database(self):
        """Restore database from backup."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Database Restore", "", "Database (*.db)"
        )
        if path:
            reply = QMessageBox.question(
                self, "Təsdiq", "Database bərpa olunacaq. Davam edilsin?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    db = DatabaseManager()
                    if db.restore_database(path):
                        QMessageBox.information(self, "Uğurlu", "Database bərpa olundu!")
                    else:
                        QMessageBox.warning(self, "Xəta", "Bərpa edilə bilmədi!")
                except Exception as e:
                    QMessageBox.critical(self, "Xəta", f"Bərpa xətası: {e}")
