"""QSS Stylesheet for dark theme."""

from config.constants import COLORS


def get_stylesheet() -> str:
    """Return the complete QSS stylesheet."""
    c = COLORS
    return f"""
    * {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }}
    QMainWindow {{
        background-color: {c['background']};
    }}
    QWidget {{
        background-color: {c['background']};
        color: {c['text_primary']};
    }}
    QWidget#sidebar {{
        background-color: {c['sidebar']};
    }}
    QWidget#card {{
        background-color: {c['card']};
        border-radius: 8px;
        border: 1px solid {c['border']};
    }}
    QWidget#header {{
        background-color: {c['sidebar']};
        border-bottom: 1px solid {c['border']};
    }}
    QLabel {{
        color: {c['text_primary']};
        background: transparent;
    }}
    QLabel#secondary {{
        color: {c['text_secondary']};
    }}
    QLabel#title {{
        font-size: 18px;
        font-weight: bold;
        color: {c['primary']};
    }}
    QLabel#stat-value {{
        font-size: 24px;
        font-weight: bold;
    }}
    QLabel#stat-label {{
        font-size: 11px;
        color: {c['text_secondary']};
    }}
    QPushButton {{
        background-color: {c['card']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {c['hover']};
        border-color: {c['primary']};
    }}
    QPushButton:pressed {{
        background-color: {c['primary']};
        color: {c['background']};
    }}
    QPushButton#primary {{
        background-color: {c['primary']};
        color: {c['background']};
        border: none;
    }}
    QPushButton#primary:hover {{
        background-color: #33ddff;
    }}
    QPushButton#danger {{
        background-color: {c['loss']};
        color: white;
        border: none;
    }}
    QPushButton#danger:hover {{
        background-color: #ff4569;
    }}
    QPushButton#success {{
        background-color: {c['profit']};
        color: {c['background']};
        border: none;
    }}
    QPushButton#sidebar-btn {{
        background: transparent;
        border: none;
        border-radius: 0px;
        padding: 12px 16px;
        text-align: left;
        font-size: 14px;
    }}
    QPushButton#sidebar-btn:hover {{
        background-color: {c['hover']};
    }}
    QPushButton#sidebar-btn:checked {{
        background-color: {c['primary']};
        color: {c['background']};
    }}
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {c['input_bg']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 6px 10px;
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border-color: {c['primary']};
    }}
    QComboBox {{
        background-color: {c['input_bg']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 6px 10px;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['input_bg']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        selection-background-color: {c['primary']};
    }}
    QSlider::groove:horizontal {{
        height: 6px;
        background: {c['border']};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {c['primary']};
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}
    QSlider::sub-page:horizontal {{
        background: {c['primary']};
        border-radius: 3px;
    }}
    QCheckBox {{
        spacing: 8px;
        color: {c['text_primary']};
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {c['border']};
        border-radius: 4px;
        background-color: {c['input_bg']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {c['primary']};
        border-color: {c['primary']};
    }}
    QTableWidget {{
        background-color: {c['card']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        gridline-color: {c['border']};
    }}
    QTableWidget::item {{
        padding: 6px;
    }}
    QTableWidget::item:selected {{
        background-color: {c['primary']};
        color: {c['background']};
    }}
    QHeaderView::section {{
        background-color: {c['sidebar']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        padding: 6px;
        font-weight: bold;
    }}
    QScrollBar:vertical {{
        background-color: {c['background']};
        width: 10px;
        border: none;
    }}
    QScrollBar::handle:vertical {{
        background-color: {c['border']};
        border-radius: 5px;
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QProgressBar {{
        background-color: {c['border']};
        border: none;
        border-radius: 4px;
        text-align: center;
        color: {c['text_primary']};
        height: 20px;
    }}
    QProgressBar::chunk {{
        background-color: {c['primary']};
        border-radius: 4px;
    }}
    QDateEdit {{
        background-color: {c['input_bg']};
        color: {c['text_primary']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 6px 10px;
    }}
    QToolTip {{
        background-color: {c['card']};
        color: {c['text_primary']};
        border: 1px solid {c['primary']};
        padding: 6px;
        border-radius: 4px;
    }}
    QStackedWidget {{
        background: transparent;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    """
