"""Statistics page with performance metrics and charts."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
)
from PyQt6.QtCore import Qt
from database.models import Signal, Trade
from database.db_manager import DatabaseManager
from gui.widgets.stat_card import StatCard
from gui.widgets.chart_widget import ChartWidget
from gui.widgets.data_table import DataTable
from config.constants import COLORS
from utils.helpers import format_percent, format_price
from datetime import date, timedelta


class StatisticsPage(QWidget):
    """Statistics page with performance metrics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the statistics page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Statistika")
        title.setObjectName("title")
        layout.addWidget(title)

        # Stat cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.total_trades_card = StatCard("Total Trades", "0")
        self.win_rate_card = StatCard("Win Rate", "0%")
        self.profit_factor_card = StatCard("Profit Factor", "0.00")
        self.max_drawdown_card = StatCard("Max Drawdown", "0%")
        self.best_trade_card = StatCard("Ən Yaxşı Trade", "$0")
        self.worst_trade_card = StatCard("Ən Pis Trade", "$0")

        stats_layout.addWidget(self.total_trades_card)
        stats_layout.addWidget(self.win_rate_card)
        stats_layout.addWidget(self.profit_factor_card)
        stats_layout.addWidget(self.max_drawdown_card)
        stats_layout.addWidget(self.best_trade_card)
        stats_layout.addWidget(self.worst_trade_card)
        layout.addLayout(stats_layout)

        # Chart toggle
        chart_row = QHBoxLayout()
        chart_label = QLabel("Qrafik:")
        chart_label.setObjectName("secondary")
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Günlük", "Həftəlik", "Aylıq"])
        self.period_combo.currentIndexChanged.connect(self.refresh)
        chart_row.addWidget(chart_label)
        chart_row.addWidget(self.period_combo)
        chart_row.addStretch()
        layout.addLayout(chart_row)

        # Charts
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(12)

        self.pnl_bar_chart = ChartWidget()
        self.pnl_bar_chart.setMinimumHeight(250)

        self.strategy_chart = ChartWidget()
        self.strategy_chart.setMinimumHeight(250)

        charts_layout.addWidget(self.pnl_bar_chart)
        charts_layout.addWidget(self.strategy_chart)
        layout.addLayout(charts_layout)

        # Tables
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(12)

        self.market_table = DataTable(["Bazar", "Trades", "Win Rate", "PnL"])
        self.market_table.setMaximumHeight(200)
        tables_layout.addWidget(self.market_table)

        self.strategy_table = DataTable(["Strategiya", "Trades", "Win Rate", "PnL"])
        self.strategy_table.setMaximumHeight(200)
        tables_layout.addWidget(self.strategy_table)
        layout.addLayout(tables_layout)

        layout.addStretch()

    def refresh(self):
        """Refresh statistics data."""
        try:
            db = DatabaseManager()
            session = db.get_session()

            trades = session.query(Trade).filter(Trade.status == "CLOSED").all()
            total = len(trades)

            if total == 0:
                session.close()
                return

            wins = [t for t in trades if (t.pnl_percent or 0) > 0]
            losses = [t for t in trades if (t.pnl_percent or 0) <= 0]
            win_rate = (len(wins) / total * 100) if total > 0 else 0

            gross_profit = sum(t.pnl or 0 for t in wins)
            gross_loss = abs(sum(t.pnl or 0 for t in losses))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

            peak = 0
            balance = 10000
            max_dd = 0
            for t in sorted(trades, key=lambda x: x.closed_at or ""):
                balance += t.pnl or 0
                peak = max(peak, balance)
                dd = (peak - balance) / peak * 100 if peak > 0 else 0
                max_dd = max(max_dd, dd)

            best = max(trades, key=lambda t: t.pnl or 0)
            worst = min(trades, key=lambda t: t.pnl or 0)

            self.total_trades_card.set_value(str(total))
            self.win_rate_card.set_value(
                f"{win_rate:.1f}%",
                COLORS["profit"] if win_rate >= 50 else COLORS["loss"]
            )
            self.profit_factor_card.set_value(
                f"{profit_factor:.2f}",
                COLORS["profit"] if profit_factor >= 1 else COLORS["loss"]
            )
            self.max_drawdown_card.set_value(f"{max_dd:.2f}%", COLORS["loss"])
            self.best_trade_card.set_value(format_price(best.pnl or 0), COLORS["profit"])
            self.worst_trade_card.set_value(format_price(worst.pnl or 0), COLORS["loss"])

            self._update_pnl_chart(trades)
            self._update_strategy_chart(trades)
            self._update_market_table(trades)
            self._update_strategy_table(trades)

            session.close()
        except Exception as e:
            print(f"Statistics refresh error: {e}")

    def _update_pnl_chart(self, trades: list):
        """Update PnL bar chart."""
        period = self.period_combo.currentText()
        if period == "Günlük":
            data, labels = self._aggregate_by_day(trades, 14)
        elif period == "Həftəlik":
            data, labels = self._aggregate_by_week(trades, 8)
        else:
            data, labels = self._aggregate_by_month(trades, 6)

        colors = [COLORS["profit"] if v >= 0 else COLORS["loss"] for v in data]
        self.pnl_bar_chart.plot_bar_chart(
            data, labels, title=f"PnL ({period})",
            colors=colors, ylabel="%"
        )

    def _aggregate_by_day(self, trades, days):
        data = []
        labels = []
        for i in range(days - 1, -1, -1):
            d = (date.today() - timedelta(days=i)).isoformat()
            day_trades = [t for t in trades if t.closed_at and t.closed_at.startswith(d)]
            pnl = sum(t.pnl_percent or 0 for t in day_trades)
            data.append(round(pnl, 2))
            labels.append((date.today() - timedelta(days=i)).strftime("%m/%d"))
        return data, labels

    def _aggregate_by_week(self, trades, weeks):
        data = []
        labels = []
        for i in range(weeks - 1, -1, -1):
            start = date.today() - timedelta(weeks=i + 1)
            end = date.today() - timedelta(weeks=i)
            week_trades = [t for t in trades if t.closed_at and
                          start.isoformat() <= t.closed_at[:10] <= end.isoformat()]
            pnl = sum(t.pnl_percent or 0 for t in week_trades)
            data.append(round(pnl, 2))
            labels.append(f"H{weeks - i}")
        return data, labels

    def _aggregate_by_month(self, trades, months):
        data = []
        labels = []
        for i in range(months - 1, -1, -1):
            month = (date.today().month - i - 1) % 12 + 1
            year = date.today().year if month <= date.today().month else date.today().year - 1
            prefix = f"{year}-{month:02d}"
            month_trades = [t for t in trades if t.closed_at and t.closed_at.startswith(prefix)]
            pnl = sum(t.pnl_percent or 0 for t in month_trades)
            data.append(round(pnl, 2))
            labels.append(f"{month:02d}/{year}")
        return data, labels

    def _update_strategy_chart(self, trades):
        """Update strategy comparison chart."""
        strategies = {}
        for t in trades:
            s = t.symbol or "Unknown"
            if s not in strategies:
                strategies[s] = {"wins": 0, "total": 0}
            strategies[s]["total"] += 1
            if (t.pnl_percent or 0) > 0:
                strategies[s]["wins"] += 1

        labels = list(strategies.keys())[:10]
        win_rates = [(strategies[s]["wins"] / strategies[s]["total"] * 100)
                     for s in labels if strategies[s]["total"] > 0]

        self.strategy_chart.plot_bar_chart(
            win_rates, labels, title="Simvollara Görə Win Rate %",
            color=COLORS["primary"], ylabel="%"
        )

    def _update_market_table(self, trades):
        """Update market statistics table."""
        markets = {}
        for t in trades:
            # Derive market from symbol
            sym = t.symbol or ""
            if sym.endswith("USDT") or sym.endswith("BTC") or sym.endswith("ETH"):
                m = "crypto"
            elif len(sym) == 6 and sym.isalpha():
                m = "forex"
            else:
                m = "stocks"
            if m not in markets:
                markets[m] = {"trades": 0, "wins": 0, "pnl": 0}
            markets[m]["trades"] += 1
            if (t.pnl_percent or 0) > 0:
                markets[m]["wins"] += 1
            markets[m]["pnl"] += t.pnl_percent or 0

        market_names = {"crypto": "Kripto", "forex": "Forex", "stocks": "Səhmlər"}
        rows = []
        for m, data in markets.items():
            wr = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
            rows.append([market_names.get(m, m), data["trades"],
                        f"{wr:.1f}%", format_percent(data["pnl"])])
        self.market_table.populate(rows)

    def _update_strategy_table(self, trades):
        """Update strategy statistics table."""
        strategies = {}
        for t in trades:
            s = t.symbol or "Unknown"
            if s not in strategies:
                strategies[s] = {"trades": 0, "wins": 0, "pnl": 0}
            strategies[s]["trades"] += 1
            if (t.pnl_percent or 0) > 0:
                strategies[s]["wins"] += 1
            strategies[s]["pnl"] += t.pnl_percent or 0

        rows = []
        for s, data in strategies.items():
            wr = (data["wins"] / data["trades"] * 100) if data["trades"] > 0 else 0
            rows.append([s, data["trades"], f"{wr:.1f}%", format_percent(data["pnl"])])
        self.strategy_table.populate(rows)
