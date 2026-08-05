"""Main window with sidebar navigation and content area."""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from gui.pages.dashboard_page import DashboardPage
from gui.pages.signals_page import SignalsPage
from gui.pages.history_page import HistoryPage
from gui.pages.statistics_page import StatisticsPage
from gui.pages.backtest_page import BacktestPage
from gui.pages.settings_page import SettingsPage
from gui.pages.about_page import AboutPage
from gui.system_tray import SystemTrayManager
from gui.styles import get_stylesheet
from core.data_fetcher import DataFetcher
from core.indicator_engine import IndicatorEngine
from core.signal_engine import SignalEngine
from core.risk_manager import RiskManager
from core.trade_executor import TradeExecutor
from core.notification_manager import NotificationManager
from database.db_manager import DatabaseManager
from database.models import Signal, Trade, User, UserSettings
from config.constants import COLORS, DATA_FETCH_INTERVALS, MARKETS, STRATEGIES
from utils.sound_player import SoundPlayer
from utils.helpers import get_signal_color
import threading
import json

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading Signal System")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(get_stylesheet())

        self.data_fetcher = DataFetcher()
        self.indicator_engine = IndicatorEngine()
        self.signal_engine = SignalEngine()
        self.sound_player = SoundPlayer()

        self.system_tray = SystemTrayManager(self)
        self.system_tray.open_clicked.connect(self._show_window)
        self.system_tray.settings_clicked.connect(lambda: self._navigate(5))
        self.system_tray.exit_clicked.connect(self._exit_app)
        self.system_tray.toggle_auto_trade.connect(self._toggle_auto_trade)

        self._setup_ui()
        self._setup_timers()
        self._refresh_all()

        self.system_tray.show()

    def _setup_ui(self):
        """Setup the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo
        logo_label = QLabel(" Trading Signal")
        logo_label.setStyleSheet(f"""
            font-size: 18px; font-weight: bold; color: {COLORS['primary']};
            padding: 20px 16px; background: transparent;
        """)
        sidebar_layout.addWidget(logo_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px;")
        sidebar_layout.addWidget(separator)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            (" Dashboard", 0),
            (" Siqnallar", 1),
            (" Tarixçə", 2),
            (" Statistika", 3),
            (" Backtest", 4),
            (" Parametrlər", 5),
            (" Haqqında", 6),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("sidebar-btn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self._navigate(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Auto trade indicator
        self.auto_label = QLabel("Auto Trade: OFF")
        self.auto_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']}; font-size: 11px;
            padding: 12px 16px; background: transparent;
        """)
        sidebar_layout.addWidget(self.auto_label)

        main_layout.addWidget(sidebar)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['primary']};")
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()

        self.status_label = QLabel("● Aktiv")
        self.status_label.setStyleSheet(f"color: {COLORS['profit']}; font-size: 12px;")
        header_layout.addWidget(self.status_label)

        content_layout.addWidget(header)

        # Stacked widget for pages
        self.stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.signals_page = SignalsPage()
        self.history_page = HistoryPage()
        self.statistics_page = StatisticsPage()
        self.backtest_page = BacktestPage()
        self.settings_page = SettingsPage()
        self.about_page = AboutPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.signals_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.statistics_page)
        self.stack.addWidget(self.backtest_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.about_page)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_widget)

        # Status bar
        self.statusBar().setStyleSheet(f"background-color: {COLORS['sidebar']}; color: {COLORS['text_secondary']};")
        self.statusBar().showMessage("Hazır")

        # Select first button
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

    def _navigate(self, index: int):
        """Navigate to a page."""
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        titles = ["Dashboard", "Siqnallar", "Tarixçə", "Statistika", "Backtest", "Parametrlər", "Haqqında"]
        self.page_title.setText(titles[index] if index < len(titles) else "")

        # Refresh page data
        page = self.stack.currentWidget()
        if hasattr(page, "refresh"):
            page.refresh()

    def _setup_timers(self):
        """Setup timers for background tasks."""
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_all)
        self.refresh_timer.start(60000)

        self.signal_timer = QTimer(self)
        self.signal_timer.timeout.connect(self._check_signals)
        self.signal_timer.start(30000)

    def _refresh_all(self):
        """Refresh all page data."""
        try:
            current = self.stack.currentWidget()
            if hasattr(current, "refresh"):
                current.refresh()

            db = DatabaseManager()
            session = db.get_session()
            active_count = session.query(Signal).filter(Signal.status == "ACTIVE").count()
            self.system_tray.set_active(active_count > 0)
            session.close()
        except Exception as e:
            logger.error(f"Refresh error: {e}")

    def _check_signals(self):
        """Background signal checking."""
        try:
            db = DatabaseManager()
            session = db.get_session()
            user = session.query(User).first()
            user_settings = session.query(UserSettings).first()

            if not user or not user_settings:
                session.close()
                return

            selected_market = user_settings.selected_market
            selected_strategy = user_settings.selected_strategy

            markets_to_check = list(MARKETS.keys()) if selected_market == "all" else [selected_market]
            strategies_to_check = list(STRATEGIES.keys()) if selected_strategy == "all" else [selected_strategy]

            from database.models import Symbol as SymbolModel, Market
            for market in markets_to_check:
                market_obj = session.query(Market).filter(Market.name == market).first()
                if not market_obj:
                    continue
                symbols = session.query(SymbolModel).filter(
                    SymbolModel.market_id == market_obj.id,
                    SymbolModel.is_active == 1
                ).all()

                for symbol in symbols:
                    for strategy_name in strategies_to_check:
                        timeframe = user_settings.timeframe
                        df = self.data_fetcher.fetch_ohlcv(symbol.symbol, timeframe, market)
                        if df is not None and not df.empty:
                            df = self.indicator_engine.calculate_all(df)
                            if df is not None:
                                signal = self.signal_engine.generate_signal(
                                    df, strategy_name, symbol.symbol, market, timeframe
                                )
                                if signal:
                                    self._handle_new_signal(signal, session, user_settings)

            session.close()
        except Exception as e:
            logger.error(f"Signal check error: {e}")

    def _handle_new_signal(self, signal_data: dict, session, user_settings=None):
        """Handle a newly generated signal."""
        try:
            risk_mgr = RiskManager(session)
            if not risk_mgr.validate_signal(signal_data):
                return
            if not risk_mgr.can_open_position(signal_data["symbol"], signal_data["signal_type"]):
                return
            if not risk_mgr.check_daily_loss_limit():
                return

            new_signal = Signal(
                symbol=signal_data["symbol"],
                market=signal_data["market"],
                strategy=signal_data["strategy"],
                signal_type=signal_data["signal_type"],
                entry_price=signal_data["entry_price"],
                stop_loss=signal_data["stop_loss"],
                take_profit_1=signal_data.get("take_profit_1"),
                take_profit_2=signal_data.get("take_profit_2"),
                take_profit_3=signal_data.get("take_profit_3"),
                risk_reward_ratio=signal_data.get("risk_reward_ratio"),
                confidence=signal_data.get("confidence", "MEDIUM"),
                timeframe=signal_data.get("timeframe", "15m"),
                status="ACTIVE",
            )
            session.add(new_signal)
            session.commit()
            signal_data["id"] = new_signal.id

            notifier = NotificationManager(session)
            notifier.send_signal_notification(signal_data)

            user = session.query(User).first()
            if user and user.auto_trade_enabled:
                executor = TradeExecutor(session)
                balance = 10000
                risk_pct = user_settings.risk_per_trade if user_settings else 1.0
                qty = risk_mgr.calculate_position_size(
                    balance, risk_pct,
                    signal_data["entry_price"], signal_data["stop_loss"]
                )
                if qty > 0:
                    executor.open_trade(signal_data, qty, is_auto=True)

            self.system_tray.show_notification(
                "Yeni Siqnal",
                f"{signal_data['signal_type']} {signal_data['symbol']} - {signal_data.get('confidence', 'MEDIUM')}"
            )

            self.sound_player.play_new_signal()
        except Exception as e:
            logger.error(f"Error handling new signal: {e}")

    def _toggle_auto_trade(self, enabled: bool):
        """Toggle auto trade."""
        try:
            db = DatabaseManager()
            session = db.get_session()
            user = session.query(User).first()
            if user:
                user.auto_trade_enabled = 1 if enabled else 0
                session.commit()
            status = "ON" if enabled else "OFF"
            self.auto_label.setText(f"Auto Trade: {status}")
            self.auto_label.setStyleSheet(f"""
                color: {COLORS['profit'] if enabled else COLORS['text_secondary']};
                font-size: 11px; padding: 12px 16px; background: transparent;
            """)
            session.close()
        except Exception as e:
            logger.error(f"Toggle auto trade error: {e}")

    def _show_window(self):
        """Show and raise the main window."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _exit_app(self):
        """Exit the application."""
        self.system_tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """Handle window close event."""
        event.ignore()
        self.hide()
        self.system_tray.show_notification(
            "Trading Signal System",
            "Proqram arxa planda işləyir. System tray-dan açın."
        )
