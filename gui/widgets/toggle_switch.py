"""Toggle switch widget for on/off settings."""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal, Qt
from config.constants import COLORS


class ToggleSwitch(QPushButton):
    """Toggle switch button."""

    toggled_state = pyqtSignal(bool)

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFixedSize(60, 30)
        self._update_style()
        self.clicked.connect(self._on_toggle)

    def _on_toggle(self):
        """Handle toggle."""
        self._checked = self.isChecked()
        self._update_style()
        self.toggled_state.emit(self._checked)

    def _update_style(self):
        """Update visual style based on state."""
        if self._checked:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['profit']};
                    border: none;
                    border-radius: 15px;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }}
            """)
            self.setText("ON")
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['border']};
                    border: none;
                    border-radius: 15px;
                    color: {COLORS['text_secondary']};
                    font-weight: bold;
                    font-size: 11px;
                }}
            """)
            self.setText("OFF")

    def is_on(self) -> bool:
        """Check if toggle is on."""
        return self._checked

    def set_state(self, checked: bool):
        """Set the toggle state."""
        self._checked = checked
        self.setChecked(checked)
        self._update_style()
