"""Chart widget using matplotlib for embedded charts."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config.constants import COLORS


class ChartWidget(QWidget):
    """Widget for displaying charts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.figure.set_facecolor(COLORS["card"])
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def plot_line_chart(self, data: list, labels: list = None, title: str = "",
                       color: str = None, xlabel: str = "", ylabel: str = ""):
        """Plot a line chart."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS["card"])
        ax.plot(data, color=color or COLORS["primary"], linewidth=2)
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, fontsize=8, color=COLORS["text_secondary"])
        ax.set_title(title, color=COLORS["text_primary"], fontsize=12, fontweight="bold")
        ax.set_xlabel(xlabel, color=COLORS["text_secondary"], fontsize=10)
        ax.set_ylabel(ylabel, color=COLORS["text_secondary"], fontsize=10)
        ax.tick_params(colors=COLORS["text_secondary"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS["border"])
        ax.spines["bottom"].set_color(COLORS["border"])
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_bar_chart(self, data: list, labels: list, title: str = "",
                      colors: list = None, xlabel: str = "", ylabel: str = ""):
        """Plot a bar chart."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS["card"])
        bar_colors = colors or [COLORS["primary"]] * len(data)
        ax.bar(range(len(data)), data, color=bar_colors)
        if labels:
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, fontsize=8, color=COLORS["text_secondary"])
        ax.set_title(title, color=COLORS["text_primary"], fontsize=12, fontweight="bold")
        ax.set_xlabel(xlabel, color=COLORS["text_secondary"], fontsize=10)
        ax.set_ylabel(ylabel, color=COLORS["text_secondary"], fontsize=10)
        ax.tick_params(colors=COLORS["text_secondary"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS["border"])
        ax.spines["bottom"].set_color(COLORS["border"])
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_pie_chart(self, data: list, labels: list, title: str = "",
                      colors: list = None):
        """Plot a pie chart."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS["card"])
        pie_colors = colors or [COLORS["profit"], COLORS["loss"], COLORS["warning"]]
        if sum(data) > 0:
            ax.pie(data, labels=labels, colors=pie_colors[:len(data)],
                   autopct="%1.1f%%", textprops={"color": COLORS["text_primary"], "fontsize": 10})
        ax.set_title(title, color=COLORS["text_primary"], fontsize=12, fontweight="bold")
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_equity_curve(self, equity: list, title: str = " Equity Curve"):
        """Plot equity curve chart."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(COLORS["card"])
        if equity:
            color = COLORS["profit"] if equity[-1] >= equity[0] else COLORS["loss"]
            ax.plot(equity, color=color, linewidth=2)
            ax.fill_between(range(len(equity)), equity, equity[0],
                          alpha=0.1, color=color)
        ax.axhline(y=equity[0] if equity else 0, color=COLORS["text_secondary"],
                   linestyle="--", alpha=0.5)
        ax.set_title(title, color=COLORS["text_primary"], fontsize=12, fontweight="bold")
        ax.set_xlabel("Trade #", color=COLORS["text_secondary"], fontsize=10)
        ax.set_ylabel("Balance ($)", color=COLORS["text_secondary"], fontsize=10)
        ax.tick_params(colors=COLORS["text_secondary"])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(COLORS["border"])
        ax.spines["bottom"].set_color(COLORS["border"])
        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        """Clear the chart."""
        self.figure.clear()
        self.canvas.draw()
