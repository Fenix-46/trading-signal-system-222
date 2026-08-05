"""Utility helper functions."""

from datetime import datetime
from typing import Union


def format_price(price: Union[float, int], decimals: int = 2) -> str:
    """Format a price value with proper separators."""
    if price is None:
        return "N/A"
    if abs(price) >= 1000:
        return f"${price:,.{decimals}f}"
    return f"${price:.{decimals}f}"


def format_percent(value: Union[float, int], decimals: int = 2) -> str:
    """Format a percentage value with sign."""
    if value is None:
        return "N/A"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def format_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M") -> str:
    """Format a datetime string."""
    if not dt_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime(fmt)
    except (ValueError, AttributeError):
        return dt_str[:16] if dt_str else "N/A"


def format_number(value: Union[float, int], decimals: int = 2) -> str:
    """Format a number with commas."""
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}"


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default: int = 0) -> int:
    """Safely convert value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_signal_color(signal_type: str) -> str:
    """Get color for signal type."""
    from config.constants import COLORS
    if signal_type == "LONG":
        return COLORS["profit"]
    elif signal_type == "SHORT":
        return COLORS["loss"]
    return COLORS["text_secondary"]


def get_pnl_color(pnl: float) -> str:
    """Get color for PnL value."""
    from config.constants import COLORS
    if pnl > 0:
        return COLORS["profit"]
    elif pnl < 0:
        return COLORS["loss"]
    return COLORS["text_secondary"]


def get_status_color(status: str) -> str:
    """Get color for signal status."""
    from config.constants import COLORS
    status_colors = {
        "ACTIVE": COLORS["primary"],
        "TP1_HIT": COLORS["profit"],
        "TP2_HIT": COLORS["profit"],
        "TP3_HIT": COLORS["profit"],
        "SL_HIT": COLORS["loss"],
        "CLOSED": COLORS["text_secondary"],
        "CANCELLED": COLORS["warning"],
    }
    return status_colors.get(status, COLORS["text_secondary"])


def calculate_rr(entry: float, sl: float, tp: float) -> float:
    """Calculate risk-reward ratio."""
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    if risk == 0:
        return 0.0
    return round(reward / risk, 2)


def truncate_string(text: str, max_length: int = 50) -> str:
    """Truncate string to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
