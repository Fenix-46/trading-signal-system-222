"""Risk slider widget for risk settings."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider
from PyQt6.QtCore import Qt, pyqtSignal
from config.constants import COLORS


class RiskSlider(QWidget):
    """Slider for risk percentage settings."""

    value_changed = pyqtSignal(float)

    def __init__(self, label: str = "Risk", min_val: float = 0.5, max_val: float = 5.0,
                 default: float = 1.0, step: float = 0.1, parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self._setup_ui(label, default)

    def _setup_ui(self, label: str, default: float):
        """Setup the slider UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        self.label = QLabel(label)
        self.label.setObjectName("secondary")
        self.value_label = QLabel(f"{default:.1f}%")
        self.value_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        top_row.addWidget(self.label)
        top_row.addStretch()
        top_row.addWidget(self.value_label)
        layout.addLayout(top_row)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(self.min_val / self.step))
        self.slider.setMaximum(int(self.max_val / self.step))
        self.slider.setValue(int(default / self.step))
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)

    def _on_value_changed(self, value: int):
        """Handle slider value change."""
        real_value = value * self.step
        self.value_label.setText(f"{real_value:.1f}%")
        self.value_changed.emit(real_value)

    def get_value(self) -> float:
        """Get current slider value."""
        return self.slider.value() * self.step

    def set_value(self, value: float):
        """Set slider value."""
        self.slider.setValue(int(value / self.step))
