"""Dashboard page with overview stats and charts."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session
from database.models import Signal, Trade
from database.db_manager import DatabaseManager
from gui.widgets.stat_card import StatCard
from gui.widgets.chart_widget import ChartWidget
from gui.widgets.data_table import DataTable
from config.constants import COLORS
from utils.helpers import format_percent, format_datetime
from datetime import date, timedelta


class DashboardPage(QWidget):
    """Dashboard page showing overview statistics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("Dashboard")
        title.setObjectName("title")
        layout.addWidget(title)

        # Stat cards row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        self.pnl_card = StatCard("Bugünkü PnL", "0.00%", COLORS["text_secondary"])
        self.total_pnl_card = StatCard("Ümumi PnL", "0.00%", COLORS["text_secondary"])
        self.active_signals_card = StatCard("Aktiv Siqnal", "0", COLORS["primary"])
        self.win_rate_card = StatCard("Win Rate", "0%", COLORS["text_secondary"])

        stats_layout.addWidget(self.pnl_card)
        stats_layout.addWidget(self.total_pnl_card)
        stats_layout.addWidget(self.active_signals_card)
        stats_layout.addWidget(self.win_rate_card)
        layout.addLayout(stats_layout)

        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(12)

        self.pnl_chart = ChartWidget()
        self.pnl_chart.setMinimumHeight(250)

        self.winloss_chart = ChartWidget()
        self.winloss_chart.setMinimumHeight(250)

        charts_layout.addWidget(self.pnl_chart)
        charts_layout.addWidget(self.winloss_chart)
        layout.addLayout(charts_layout)

        # Recent signals table
        recent_label = QLabel("Son 10 Siqnal")
        recent_label.setObjectName("secondary")
        layout.addWidget(recent_label)

        self.recent_table = DataTable(
            ["Vaxt", "Simvol", "Bazar", "Tip", "Giriş", "SL", "TP", "Status", "PnL"]
        )
        self.recent_table.setMaximumHeight(300)
        layout.addWidget(self.recent_table)

        layout.addStretch()

    def refresh(self):
        """Refresh dashboard data."""
        try:
            db = DatabaseManager()
            session = db.get_session()

            today = date.today().isoformat()
            today_trades = session.query(Trade).filter(
                Trade.closed_at.like(f"{today}%"),
                Trade.status == "CLOSED"
            ).all()

            daily_pnl = sum(t.pnl_percent or 0 for t in today_trades)
            self.pnl_card.set_value(
                format_percent(daily_pnl),
                COLORS["profit"] if daily_pnl >= 0 else COLORS["loss"]
            )

            all_trades = session.query(Trade).filter(Trade.status == "CLOSED").all()
            total_pnl = sum(t.pnl_percent or 0 for t in all_trades)
            self.total_pnl_card.set_value(
                format_percent(total_pnl),
                COLORS["profit"] if total_pnl >= 0 else COLORS["loss"]
            )

            active_count = session.query(Signal).filter(Signal.status == "ACTIVE").count()
            self.active_signals_card.set_value(str(active_count))

            if all_trades:
                wins = sum(1 for t in all_trades if (t.pnl_percent or 0) > 0)
                win_rate = (wins / len(all_trades)) * 100
            else:
                win_rate = 0
            self.win_rate_card.set_value(
                f"{win_rate:.1f}%",
                COLORS["profit"] if win_rate >= 50 else COLORS["loss"]
            )

            self._update_pnl_chart(session)
            self._update_winloss_chart(all_trades)
            self._update_recent_signals(session)

            session.close()
        except Exception as e:
            print(f"Dashboard refresh error: {e}")

    def _update_pnl_chart(self, session: Session):
        """Update PnL line chart."""
        days = []
        pnls = []
        for i in range(29, -1, -1):
            d = (date.today() - timedelta(days=i)).isoformat()
            trades = session.query(Trade).filter(
                Trade.closed_at.like(f"{d}%"),
                Trade.status == "CLOSED"
            ).all()
            daily_pnl = sum(t.pnl_percent or 0 for t in trades)
            days.append((date.today() - timedelta(days=i)).strftime("%m/%d"))
            pnls.append(round(daily_pnl, 2))
        self.pnl_chart.plot_line_chart(
            pnls, days, title="PnL (Son 30 Gün)",
            color=COLORS["profit"], ylabel="%"
        )

    def _update_winloss_chart(self, trades: list):
        """Update win/loss pie chart."""
        wins = sum(1 for t in trades if (t.pnl_percent or 0) > 0)
        losses = sum(1 for t in trades if (t.pnl_percent or 0) < 0)
        if wins + losses > 0:
            self.winloss_chart.plot_pie_chart(
                [wins, losses],
                [f"Qazanan ({wins})", f"Uduzan ({losses})"],
                title="Win/Loss Nisbəti",
                colors=[COLORS["profit"], COLORS["loss"]]
            )

    def _update_recent_signals(self, session: Session):
        """Update recent signals table."""
        signals = session.query(Signal).order_by(Signal.created_at.desc()).limit(10).all()
        rows = []
        for s in signals:
            rows.append([
                format_datetime(s.created_at) if s.created_at else "",
                s.symbol or "",
                s.market or "",
                s.signal_type or "",
                f"${s.entry_price:,.2f}" if s.entry_price else "",
                f"${s.stop_loss:,.2f}" if s.stop_loss else "",
                f"${s.take_profit_1:,.2f}" if s.take_profit_1 else "",
                s.status or "",
                format_percent(s.pnl_percent) if s.pnl_percent else "N/A",
            ])
        status_colors = {
            "ACTIVE": COLORS["primary"],
            "TP1_HIT": COLORS["profit"], "TP2_HIT": COLORS["profit"],
            "TP3_HIT": COLORS["profit"], "SL_HIT": COLORS["loss"],
        }
        colored_cols = {7: status_colors, 3: {"LONG": COLORS["profit"], "SHORT": COLORS["loss"]}}
        self.recent_table.populate(rows, colored_cols)
