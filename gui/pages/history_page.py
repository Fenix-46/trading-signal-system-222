"""History page showing all past signals in a table."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt
from database.models import Signal
from database.db_manager import DatabaseManager
from gui.widgets.data_table import DataTable
from gui.widgets.filter_bar import FilterBar
from config.constants import COLORS
from utils.helpers import format_price, format_percent, format_datetime
import csv


class HistoryPage(QWidget):
    """History page with full signal table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the history page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Tarixçə")
        title.setObjectName("title")
        layout.addWidget(title)

        self.filter_bar = FilterBar()
        self.filter_bar.filter_changed.connect(self.refresh)
        self.filter_bar.refresh_clicked.connect(self.refresh)
        layout.addWidget(self.filter_bar)

        top_row = QHBoxLayout()
        self.count_label = QLabel("0 siqnal")
        self.count_label.setObjectName("secondary")
        top_row.addWidget(self.count_label)
        top_row.addStretch()

        export_btn = QPushButton("Export CSV")
        export_btn.setObjectName("primary")
        export_btn.clicked.connect(self._export_csv)
        top_row.addWidget(export_btn)
        layout.addLayout(top_row)

        self.table = DataTable(
            ["ID", "Vaxt", "Simvol", "Bazar", "Strategiya", "Tip",
             "Giriş", "SL", "TP1", "TP2", "TP3", "R:R", "Confidence",
             "Status", "PnL%"]
        )
        layout.addWidget(self.table)

        self.all_signals = []

    def refresh(self):
        """Refresh history data."""
        try:
            db = DatabaseManager()
            session = db.get_session()

            filters = self.filter_bar.get_filters()
            query = session.query(Signal)

            if filters["market"] != "all":
                query = query.filter(Signal.market == filters["market"])
            if filters["strategy"] != "all":
                query = query.filter(Signal.strategy == filters["strategy"])
            if filters["status"] != "all":
                query = query.filter(Signal.status == filters["status"])

            signals = query.order_by(Signal.created_at.desc()).all()
            self.all_signals = signals
            self.count_label.setText(f"{len(signals)} siqnal")

            rows = []
            for s in signals:
                rows.append([
                    s.id,
                    format_datetime(s.created_at) if s.created_at else "",
                    s.symbol or "",
                    s.market or "",
                    s.strategy or "",
                    s.signal_type or "",
                    format_price(s.entry_price),
                    format_price(s.stop_loss),
                    format_price(s.take_profit_1),
                    format_price(s.take_profit_2),
                    format_price(s.take_profit_3),
                    f"1:{s.risk_reward_ratio:.1f}" if s.risk_reward_ratio else "",
                    s.confidence or "",
                    s.status or "",
                    format_percent(s.pnl_percent) if s.pnl_percent else "N/A",
                ])

            status_colors = {
                "ACTIVE": COLORS["primary"],
                "TP1_HIT": COLORS["profit"], "TP2_HIT": COLORS["profit"],
                "TP3_HIT": COLORS["profit"], "SL_HIT": COLORS["loss"],
            }
            colored_cols = {
                5: {"LONG": COLORS["profit"], "SHORT": COLORS["loss"]},
                13: status_colors,
            }
            self.table.populate(rows, colored_cols)
            session.close()
        except Exception as e:
            print(f"History refresh error: {e}")

    def _export_csv(self):
        """Export signals to CSV file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "CSV Export", "signals_export.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Vaxt", "Simvol", "Bazar", "Strategiya", "Tip",
                               "Giriş", "SL", "TP1", "TP2", "TP3", "R:R",
                               "Confidence", "Status", "PnL%"])
                for s in self.all_signals:
                    writer.writerow([
                        s.id, format_datetime(s.created_at), s.symbol, s.market,
                        s.strategy, s.signal_type, s.entry_price, s.stop_loss,
                        s.take_profit_1, s.take_profit_2, s.take_profit_3,
                        s.risk_reward_ratio, s.confidence, s.status, s.pnl_percent
                    ])
        except Exception as e:
            print(f"Export error: {e}")
