"""Application constants."""

APP_NAME = "Trading Signal System"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Universal Trading"

COLORS = {
    "background": "#1a1a2e",
    "sidebar": "#16213e",
    "card": "#0f3460",
    "primary": "#00d4ff",
    "profit": "#00e676",
    "loss": "#ff1744",
    "warning": "#ffab00",
    "text_primary": "#ffffff",
    "text_secondary": "#b0b0b0",
    "border": "#1e3a5f",
    "input_bg": "#1a2740",
    "hover": "#1a3a6e",
}

MARKETS = {
    "crypto": "Kripto",
    "forex": "Forex",
    "stocks": "Səhmlər",
}

STRATEGIES = {
    "scalping": "Scalping",
    "day_trading": "Day Trading",
    "swing": "Swing Trading",
    "trend_following": "Trend Following",
}

TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1D"]

TIMEFRAME_INTERVALS = {
    "scalping": ["1m", "5m"],
    "day_trading": ["15m", "1h"],
    "swing": ["4h", "1D"],
    "trend_following": ["4h", "1D"],
}

DATA_FETCH_INTERVALS = {
    "scalping": 30,
    "day_trading": 60,
    "swing": 300,
    "trend_following": 900,
}

CONFIDENCE_LEVELS = {
    "HIGH": "HIGH",
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
}

SIGNAL_TYPES = {
    "LONG": "LONG",
    "SHORT": "SHORT",
}

SIGNAL_STATUSES = {
    "ACTIVE": "ACTIVE",
    "TP1_HIT": "TP1_HIT",
    "TP2_HIT": "TP2_HIT",
    "TP3_HIT": "TP3_HIT",
    "SL_HIT": "SL_HIT",
    "CLOSED": "CLOSED",
    "CANCELLED": "CANCELLED",
}

TRADE_STATUSES = {
    "OPEN": "OPEN",
    "CLOSED": "CLOSED",
    "CANCELLED": "CANCELLED",
}

DEFAULT_CRYPTO_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT",
]

DEFAULT_FOREX_SYMBOLS = [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD",
    "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY",
]

DEFAULT_STOCK_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META",
    "TSLA", "NVDA", "JPM", "V", "JNJ",
]

DEFAULT_SETTINGS = {
    "selected_market": "all",
    "selected_strategy": "all",
    "selected_symbols": "[]",
    "risk_per_trade": 1.0,
    "max_open_positions": 3,
    "timeframe": "15m",
    "daily_loss_limit": 5.0,
    "notifications_enabled": 1,
    "sound_enabled": 1,
    "theme": "dark",
    "auto_trade_enabled": 0,
    "start_with_windows": 0,
    "minimize_to_tray": 1,
}
