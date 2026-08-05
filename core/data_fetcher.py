"""Data fetcher for multiple markets."""

import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class DataFetcher:
    """Fetches market data from multiple sources."""

    def __init__(self):
        self._ccxt_exchange = None
        self._cache: Dict[str, pd.DataFrame] = {}
        self._cache_time: Dict[str, float] = {}
        self._cache_ttl = 60

    def _get_ccxt_exchange(self):
        """Initialize ccxt Binance exchange."""
        if self._ccxt_exchange is None:
            try:
                import ccxt
                self._ccxt_exchange = ccxt.binance({
                    "enableRateLimit": True,
                    "options": {"defaultType": "spot"}
                })
            except Exception as e:
                logger.error(f"Error initializing ccxt: {e}")
        return self._ccxt_exchange

    def _get_cache_key(self, symbol: str, timeframe: str, market: str) -> str:
        """Generate cache key."""
        return f"{market}:{symbol}:{timeframe}"

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache is still valid."""
        if key not in self._cache_time:
            return False
        return (time.time() - self._cache_time[key]) < self._cache_ttl

    def fetch_ohlcv(self, symbol: str, timeframe: str, market: str,
                    limit: int = 200) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data for a symbol."""
        cache_key = self._get_cache_key(symbol, timeframe, market)
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)

        try:
            if market == "crypto":
                df = self._fetch_crypto(symbol, timeframe, limit)
            elif market == "forex":
                df = self._fetch_forex(symbol, timeframe, limit)
            elif market == "stocks":
                df = self._fetch_stocks(symbol, timeframe, limit)
            else:
                logger.warning(f"Unknown market: {market}")
                return None

            if df is not None and not df.empty:
                self._cache[cache_key] = df
                self._cache_time[cache_key] = time.time()
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol} ({market}): {e}")
            return None

    def _fetch_crypto(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Fetch crypto data using ccxt."""
        try:
            exchange = self._get_ccxt_exchange()
            if exchange is None:
                return self._generate_mock_data(symbol, timeframe, limit)

            ccxt_timeframe = self._convert_timeframe_ccxt(timeframe)
            ohlcv = exchange.fetch_ohlcv(symbol, ccxt_timeframe, limit=limit)
            if not ohlcv:
                return self._generate_mock_data(symbol, timeframe, limit)

            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching crypto data: {e}")
            return self._generate_mock_data(symbol, timeframe, limit)

    def _fetch_forex(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Fetch forex data using yfinance."""
        try:
            import yfinance as yf
            yf_symbol = f"{symbol}=X" if not symbol.endswith("=X") else symbol
            interval = self._convert_timeframe_yfinance(timeframe)
            period = self._get_yfinance_period(timeframe, limit)
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                return self._generate_mock_data(symbol, timeframe, limit)
            df.columns = [c.lower() for c in df.columns]
            if "adj close" in df.columns:
                df.drop(columns=["adj close"], inplace=True, errors="ignore")
            df.drop(columns=["dividends", "stock splits"], inplace=True, errors="ignore")
            return df
        except Exception as e:
            logger.error(f"Error fetching forex data: {e}")
            return self._generate_mock_data(symbol, timeframe, limit)

    def _fetch_stocks(self, symbol: str, timeframe: str, limit: int) -> Optional[pd.DataFrame]:
        """Fetch stock data using yfinance."""
        try:
            import yfinance as yf
            interval = self._convert_timeframe_yfinance(timeframe)
            period = self._get_yfinance_period(timeframe, limit)
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                return self._generate_mock_data(symbol, timeframe, limit)
            df.columns = [c.lower() for c in df.columns]
            if "adj close" in df.columns:
                df.drop(columns=["adj close"], inplace=True, errors="ignore")
            df.drop(columns=["dividends", "stock splits"], inplace=True, errors="ignore")
            return df
        except Exception as e:
            logger.error(f"Error fetching stock data: {e}")
            return self._generate_mock_data(symbol, timeframe, limit)

    def _generate_mock_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Generate mock OHLCV data for testing."""
        np.random.seed(hash(symbol) % 2**31)
        base_price = self._get_base_price(symbol)
        dates = pd.date_range(end=datetime.now(), periods=limit, freq=self._timeframe_to_pandas_freq(timeframe))
        returns = np.random.normal(0.0001, 0.015, limit)
        prices = base_price * np.exp(np.cumsum(returns))
        df = pd.DataFrame({
            "open": prices * (1 + np.random.uniform(-0.005, 0.005, limit)),
            "high": prices * (1 + np.abs(np.random.normal(0, 0.01, limit))),
            "low": prices * (1 - np.abs(np.random.normal(0, 0.01, limit))),
            "close": prices,
            "volume": np.random.uniform(1000, 100000, limit),
        }, index=dates)
        df.index.name = "timestamp"
        return df

    def _get_base_price(self, symbol: str) -> float:
        """Get base price for mock data generation."""
        prices = {
            "BTCUSDT": 64000, "ETHUSDT": 3400, "BNBUSDT": 600,
            "SOLUSDT": 140, "XRPUSDT": 0.62, "ADAUSDT": 0.58,
            "DOGEUSDT": 0.12, "AVAXUSDT": 35, "DOTUSDT": 7.5,
            "LINKUSDT": 14.5, "EURUSD": 1.0850, "GBPUSD": 1.2650,
            "USDJPY": 149.50, "USDCHF": 0.8750, "AUDUSD": 0.6550,
            "USDCAD": 1.3650, "NZDUSD": 0.6100, "EURGBP": 0.8580,
            "EURJPY": 162.0, "GBPJPY": 189.0, "AAPL": 178,
            "MSFT": 378, "GOOGL": 140, "AMZN": 178, "META": 505,
            "TSLA": 245, "NVDA": 880, "JPM": 195, "V": 278, "JNJ": 156,
        }
        return prices.get(symbol, 100.0)

    def _convert_timeframe_ccxt(self, tf: str) -> str:
        """Convert timeframe to ccxt format."""
        mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1D": "1d"}
        return mapping.get(tf, "15m")

    def _convert_timeframe_yfinance(self, tf: str) -> str:
        """Convert timeframe to yfinance interval format."""
        mapping = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "1h", "1D": "1d"}
        return mapping.get(tf, "15m")

    def _get_yfinance_period(self, tf: str, limit: int) -> str:
        """Get yfinance period string."""
        if tf in ["1m", "5m", "15m"]:
            return "5d"
        elif tf in ["1h", "4h"]:
            return "60d"
        else:
            return "1y"

    def _timeframe_to_pandas_freq(self, tf: str) -> str:
        """Convert timeframe to pandas frequency string."""
        mapping = {"1m": "1min", "5m": "5min", "15m": "15min",
                   "1h": "1h", "4h": "4h", "1D": "1D"}
        return mapping.get(tf, "15min")

    def get_current_price(self, symbol: str, market: str) -> Optional[float]:
        """Get current price for a symbol."""
        try:
            if market == "crypto":
                exchange = self._get_ccxt_exchange()
                if exchange:
                    ticker = exchange.fetch_ticker(symbol)
                    return ticker.get("last")
            elif market in ["forex", "stocks"]:
                import yfinance as yf
                yf_symbol = f"{symbol}=X" if market == "forex" and not symbol.endswith("=X") else symbol
                ticker = yf.Ticker(yf_symbol)
                info = ticker.fast_info
                return info.get("lastPrice") or info.get("previousClose")
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
        return None
