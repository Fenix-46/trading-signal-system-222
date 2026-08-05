"""SQLAlchemy ORM models for the trading signal system."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, Float, Text, ForeignKey,
    create_engine, DateTime
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(Text, unique=True, nullable=False)
    telegram_chat_id = Column(Text, nullable=True)
    telegram_bot_token = Column(Text, nullable=True)
    auto_trade_enabled = Column(Integer, default=0)
    created_at = Column(Text, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(Text, default=lambda: datetime.utcnow().isoformat(),
                        onupdate=lambda: datetime.utcnow().isoformat())

    settings = relationship("UserSettings", back_populates="user", uselist=False)


class Market(Base):
    """Market model."""
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    display_name = Column(Text, nullable=False)
    is_active = Column(Integer, default=1)

    symbols = relationship("Symbol", back_populates="market")


class Symbol(Base):
    """Symbol model."""
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    symbol = Column(Text, nullable=False)
    display_name = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)

    market = relationship("Market", back_populates="symbols")


class Strategy(Base):
    """Strategy model."""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True, nullable=False)
    display_name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)


class UserSettings(Base):
    """User settings model."""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    selected_market = Column(Text, default="all")
    selected_strategy = Column(Text, default="all")
    selected_symbols = Column(Text, default="[]")
    risk_per_trade = Column(Float, default=1.0)
    max_open_positions = Column(Integer, default=3)
    timeframe = Column(Text, default="15m")
    daily_loss_limit = Column(Float, default=5.0)
    notifications_enabled = Column(Integer, default=1)
    sound_enabled = Column(Integer, default=1)
    theme = Column(Text, default="dark")
    updated_at = Column(Text, default=lambda: datetime.utcnow().isoformat())

    user = relationship("User", back_populates="settings")


class Signal(Base):
    """Signal model."""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(Text, nullable=False)
    market = Column(Text, nullable=False)
    strategy = Column(Text, nullable=False)
    signal_type = Column(Text, nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit_1 = Column(Float, nullable=True)
    take_profit_2 = Column(Float, nullable=True)
    take_profit_3 = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)
    confidence = Column(Text, default="MEDIUM")
    timeframe = Column(Text, default="15m")
    status = Column(Text, default="ACTIVE")
    pnl_percent = Column(Float, nullable=True)
    entry_time = Column(Text, default=lambda: datetime.utcnow().isoformat())
    exit_time = Column(Text, nullable=True)
    exit_price = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(Text, default=lambda: datetime.utcnow().isoformat())

    notifications = relationship("NotificationLog", back_populates="signal")


class Trade(Base):
    """Trade model."""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)
    symbol = Column(Text, nullable=False)
    side = Column(Text, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    status = Column(Text, default="OPEN")
    is_auto = Column(Integer, default=0)
    opened_at = Column(Text, default=lambda: datetime.utcnow().isoformat())
    closed_at = Column(Text, nullable=True)


class NotificationLog(Base):
    """Notification log model."""
    __tablename__ = "notifications_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=True)
    message = Column(Text, nullable=False)
    channel = Column(Text, nullable=False)
    status = Column(Text, default="SENT")
    sent_at = Column(Text, default=lambda: datetime.utcnow().isoformat())

    signal = relationship("Signal", back_populates="notifications")


class BacktestResult(Base):
    """Backtest result model."""
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    strategy = Column(Text, nullable=False)
    symbol = Column(Text, nullable=False)
    timeframe = Column(Text, nullable=False)
    start_date = Column(Text, nullable=False)
    end_date = Column(Text, nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    total_pnl_percent = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    created_at = Column(Text, default=lambda: datetime.utcnow().isoformat())
