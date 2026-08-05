"""Seed initial data into the database."""

import json
import logging
from database.db_manager import DatabaseManager
from database.models import Market, Symbol, Strategy, User, UserSettings
from config.constants import (
    DEFAULT_CRYPTO_SYMBOLS, DEFAULT_FOREX_SYMBOLS,
    DEFAULT_STOCK_SYMBOLS, MARKETS, STRATEGIES
)

logger = logging.getLogger(__name__)


def seed_database():
    """Seed the database with initial data."""
    db = DatabaseManager()
    session = db.get_session()
    try:
        _seed_markets(session)
        _seed_symbols(session)
        _seed_strategies(session)
        _seed_user(session)
        session.commit()
        logger.info("Database seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding database: {e}")
        raise
    finally:
        session.close()


def _seed_markets(session):
    """Seed market data."""
    existing = session.query(Market).count()
    if existing > 0:
        return
    for name, display_name in MARKETS.items():
        market = Market(name=name, display_name=display_name, is_active=1)
        session.add(market)
    session.flush()
    logger.info("Markets seeded.")


def _seed_symbols(session):
    """Seed symbol data."""
    existing = session.query(Symbol).count()
    if existing > 0:
        return
    markets = {m.name: m.id for m in session.query(Market).all()}
    symbol_data = {
        "crypto": DEFAULT_CRYPTO_SYMBOLS,
        "forex": DEFAULT_FOREX_SYMBOLS,
        "stocks": DEFAULT_STOCK_SYMBOLS,
    }
    for market_name, symbols in symbol_data.items():
        market_id = markets.get(market_name)
        if market_id:
            for sym in symbols:
                symbol = Symbol(
                    market_id=market_id,
                    symbol=sym,
                    display_name=sym,
                    is_active=1
                )
                session.add(symbol)
    session.flush()
    logger.info("Symbols seeded.")


def _seed_strategies(session):
    """Seed strategy data."""
    existing = session.query(Strategy).count()
    if existing > 0:
        return
    descriptions = {
        "scalping": "Qısa müddətli trades, sürətli giriş/çıxış",
        "day_trading": "Gündəlik trades, eyni gün bağlanır",
        "swing": "Orta müddətli trades, bir neçə gün açıq qalır",
        "trend_following": "Trend istiqamətində uzun müddətli trades",
    }
    for name, display_name in STRATEGIES.items():
        strategy = Strategy(
            name=name,
            display_name=display_name,
            description=descriptions.get(name, ""),
            is_active=1
        )
        session.add(strategy)
    session.flush()
    logger.info("Strategies seeded.")


def _seed_user(session):
    """Seed default user."""
    existing = session.query(User).count()
    if existing > 0:
        return
    user = User(username="default", auto_trade_enabled=0)
    session.add(user)
    session.flush()
    settings = UserSettings(
        user_id=user.id,
        selected_market="all",
        selected_strategy="all",
        selected_symbols=json.dumps([]),
        risk_per_trade=1.0,
        max_open_positions=3,
        timeframe="15m",
        daily_loss_limit=5.0,
        notifications_enabled=1,
        sound_enabled=1,
        theme="dark",
    )
    session.add(settings)
    session.flush()
    logger.info("Default user seeded.")
