"""Backtest page for strategy testing."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDateEdit, QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from gui.widgets.chart_widget import ChartWidget
from gui.widgets.stat_card import StatCard
from gui.widgets.data_table import DataTable
from gui.widgets.progress_dialog import ProgressDialog
from core.backtest_engine import BacktestEngine
from database.db_manager import DatabaseManager
from config.constants import COLORS, DEFAULT_CRYPTO_SYMBOLS, TIMEFRAMES, STRATEGIES
from utils.helpers import format_price, format_percent


class BacktestWorker(QThread):
    """Worker thread for running backtest."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, symbol, strategy, timeframe, start_date, end_date):
        super().__init__()
        self.symbol = symbol
        self.strategy = strategy
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        try:
            engine = BacktestEngine()
            result = engine.run_backtest(
                self.symbol, self.strategy, self.timeframe,
                self.start_date, self.end_date
            )
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("Backtest nəticəsi alınamadı")
        except Exception as e:
            self.error.emit(str(e))


class BacktestPage(QWidget):
    """Backtest page for strategy testing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the backtest page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Backtest")
        title.setObjectName("title")
        layout.addWidget(title)

        # Parameters
        params_card = QWidget()
        params_card.setObjectName("card")
        params_layout = QGridLayout(params_card)
        params_layout.setSpacing(12)

        # Symbol
        sym_label = QLabel("Simvol:")
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(DEFAULT_CRYPTO_SYMBOLS)
        self.symbol_combo.setEditable(True)
        self.symbol_combo.setFixedWidth(150)

        # Strategy
        strat_label = QLabel("Strategiya:")
        self.strategy_combo = QComboBox()
        for name, display in STRATEGIES.items():
            self.strategy_combo.addItem(display, name)
        self.strategy_combo.setFixedWidth(150)

        # Timeframe
        tf_label = QLabel("Timeframe:")
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(TIMEFRAMES)
        self.timeframe_combo.setFixedWidth(100)

        # Start date
        start_label = QLabel("Başlanğıc:")
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setFixedWidth(150)

        # End date
        end_label = QLabel("Son:")
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setFixedWidth(150)

        # Run button
        self.run_btn = QPushButton("Backtest Başlat")
        self.run_btn.setObjectName("primary")
        self.run_btn.setFixedWidth(150)
        self.run_btn.clicked.connect(self._run_backtest)

        params_layout.addWidget(sym_label, 0, 0)
        params_layout.addWidget(self.symbol_combo, 0, 1)
        params_layout.addWidget(strat_label, 0, 2)
        params_layout.addWidget(self.strategy_combo, 0, 3)
        params_layout.addWidget(tf_label, 0, 4)
        params_layout.addWidget(self.timeframe_combo, 0, 5)
        params_layout.addWidget(start_label, 1, 0)
        params_layout.addWidget(self.start_date, 1, 1)
        params_layout.addWidget(end_label, 1, 2)
        params_layout.addWidget(self.end_date, 1, 3)
        params_layout.addWidget(self.run_btn, 1, 5)
        layout.addWidget(params_card)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results
        self.results_widget = QWidget()
        results_layout = QVBoxLayout(self.results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)
        self.bt_trades_card = StatCard("Total Trades", "0")
        self.bt_winrate_card = StatCard("Win Rate", "0%")
        self.bt_pnl_card = StatCard("Total PnL", "0%")
        self.bt_drawdown_card = StatCard("Max Drawdown", "0%")
        self.bt_sharpe_card = StatCard("Sharpe Ratio", "0")
        self.bt_pf_card = StatCard("Profit Factor", "0")

        stats_layout.addWidget(self.bt_trades_card)
        stats_layout.addWidget(self.bt_winrate_card)
        stats_layout.addWidget(self.bt_pnl_card)
        stats_layout.addWidget(self.bt_drawdown_card)
        stats_layout.addWidget(self.bt_sharpe_card)
        stats_layout.addWidget(self.bt_pf_card)
        results_layout.addLayout(stats_layout)

        self.equity_chart = ChartWidget()
        self.equity_chart.setMinimumHeight(250)
        results_layout.addWidget(self.equity_chart)

        self.trades_table = DataTable(
            ["#", "Tip", "Giriş", "Çıxış", "Nəticə", "PnL"]
        )
        self.trades_table.setMaximumHeight(250)
        results_layout.addWidget(self.trades_table)

        self.results_widget.setVisible(False)
        layout.addWidget(self.results_widget)
        layout.addStretch()

    def _run_backtest(self):
        """Start backtest."""
        self.run_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.results_widget.setVisible(False)

        symbol = self.symbol_combo.currentText()
        strategy = self.strategy_combo.currentData()
        timeframe = self.timeframe_combo.currentText()
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")

        self.worker = BacktestWorker(symbol, strategy, timeframe, start, end)
        self.worker.finished.connect(self._on_backtest_done)
        self.worker.error.connect(self._on_backtest_error)
        self.worker.start()

    def _on_backtest_done(self, result):
        """Handle backtest completion."""
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        self.results_widget.setVisible(True)

        self.bt_trades_card.set_value(str(result["total_trades"]))
        self.bt_winrate_card.set_value(
            f"{result['win_rate']:.1f}%",
            COLORS["profit"] if result["win_rate"] >= 50 else COLORS["loss"]
        )
        self.bt_pnl_card.set_value(
            format_percent(result["total_pnl_percent"]),
            COLORS["profit"] if result["total_pnl_percent"] >= 0 else COLORS["loss"]
        )
        self.bt_drawdown_card.set_value(f"{result['max_drawdown']:.2f}%", COLORS["loss"])
        self.bt_sharpe_card.set_value(f"{result['sharpe_ratio']:.2f}")
        self.bt_pf_card.set_value(
            f"{result['profit_factor']:.2f}",
            COLORS["profit"] if result["profit_factor"] >= 1 else COLORS["loss"]
        )

        equity = result.get("equity_curve", [])
        if equity:
            self.equity_chart.plot_equity_curve(equity, title=" Equity Curve")

        trades = result.get("trades", [])
        rows = []
        for i, t in enumerate(trades):
            rows.append([
                i + 1,
                t.get("type", ""),
                format_price(t.get("entry", 0)),
                format_price(t.get("exit", 0)),
                t.get("result", ""),
                format_price(t.get("pnl", 0)),
            ])
        result_colors = {"WIN": COLORS["profit"], "LOSS": COLORS["loss"]}
        colored_cols = {4: result_colors, 5: {
            "WIN": COLORS["profit"], "LOSS": COLORS["loss"]
        }}
        self.trades_table.populate(rows, colored_cols)

        # Save to database
        try:
            db = DatabaseManager()
            session = db.get_session()
            engine = BacktestEngine()
            engine.save_result(session, result)
            session.close()
        except Exception as e:
            print(f"Error saving backtest result: {e}")

    def _on_backtest_error(self, error):
        """Handle backtest error."""
        self.progress_bar.setVisible(False)
        self.run_btn.setEnabled(True)
        print(f"Backtest error: {error}")
