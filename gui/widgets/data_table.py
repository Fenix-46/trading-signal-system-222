"""Data table widget for displaying tabular data."""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from config.constants import COLORS


class DataTable(QTableWidget):
    """Custom table widget with sorting and styling."""

    def __init__(self, columns: list, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSortingEnabled(True)

        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(120)

    def populate(self, rows: list, colored_columns: dict = None):
        """Populate table with data rows."""
        self.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if colored_columns and j in colored_columns:
                    color = colored_columns[j].get(str(value), None)
                    if color:
                        item.setForeground(QColor(color))
                self.setItem(i, j, item)
        self.resizeColumnsToContents()

    def clear_data(self):
        """Clear all table data."""
        self.setRowCount(0)

    def get_selected_row(self) -> int:
        """Get index of selected row."""
        rows = self.selectionModel().selectedRows()
        if rows:
            return rows[0].row()
        return -1
