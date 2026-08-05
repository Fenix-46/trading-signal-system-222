"""Technical indicator calculation engine."""

import logging
from typing import Dict, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class IndicatorEngine:
    """Calculates technical indicators for trading signals."""

    def calculate_all(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Calculate all indicators on a DataFrame."""
        if df is None or df.empty or len(df) < 50:
            return None
        try:
            df = df.copy()
            df = self._ema(df)
            df = self._rsi(df)
            df = self._macd(df)
            df = self._bollinger_bands(df)
            df = self._stochastic(df)
            df = self._adx(df)
            df = self._atr(df)
            df = self._volume_sma(df)
            df = self._supertrend(df)
            df = df.dropna()
            return df
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return None

    def _ema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Exponential Moving Averages."""
        for period in [9, 20, 21, 50, 200]:
            df[f"ema_{period}"] = df["close"].ewm(span=period, adjust=False).mean()
        return df

    def _rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index."""
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))
        return df

    def _macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """Calculate MACD."""
        ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
        ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
        df["macd"] = ema_fast - ema_slow
        df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
        df["macd_histogram"] = df["macd"] - df["macd_signal"]
        return df

    def _bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Calculate Bollinger Bands."""
        sma = df["close"].rolling(window=period).mean()
        std = df["close"].rolling(window=period).std()
        df["bb_upper"] = sma + (std * std_dev)
        df["bb_middle"] = sma
        df["bb_lower"] = sma - (std * std_dev)
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
        return df

    def _stochastic(self, df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """Calculate Stochastic Oscillator."""
        low_min = df["low"].rolling(window=k_period).min()
        high_max = df["high"].rolling(window=k_period).max()
        df["stoch_k"] = 100 * (df["close"] - low_min) / (high_max - low_min)
        df["stoch_d"] = df["stoch_k"].rolling(window=d_period).mean()
        return df

    def _adx(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average Directional Index."""
        high = df["high"]
        low = df["low"]
        close = df["close"]
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        plus_dm[(plus_dm < minus_dm)] = 0
        minus_dm[(minus_dm < plus_dm)] = 0
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        atr = tr.ewm(span=period, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(span=period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(span=period, adjust=False).mean() / atr)
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
        df["adx"] = dx.ewm(span=period, adjust=False).mean()
        df["plus_di"] = plus_di
        df["minus_di"] = minus_di
        return df

    def _atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range."""
        high = df["high"]
        low = df["low"]
        close = df["close"]
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        df["atr"] = tr.ewm(span=period, adjust=False).mean()
        return df

    def _volume_sma(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Volume Simple Moving Average."""
        df["volume_sma"] = df["volume"].rolling(window=period).mean()
        df["volume_ratio"] = df["volume"] / df["volume_sma"]
        return df

    def _supertrend(self, df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        """Calculate Supertrend indicator."""
        hl2 = (df["high"] + df["low"]) / 2
        atr = df["atr"] if "atr" in df.columns else self._calculate_basic_atr(df, period)
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        supertrend = pd.Series(index=df.index, dtype=float)
        direction = pd.Series(index=df.index, dtype=int)
        supertrend.iloc[0] = upper_band.iloc[0]
        direction.iloc[0] = -1
        for i in range(1, len(df)):
            if df["close"].iloc[i] > upper_band.iloc[i - 1]:
                direction.iloc[i] = 1
            elif df["close"].iloc[i] < lower_band.iloc[i - 1]:
                direction.iloc[i] = -1
            else:
                direction.iloc[i] = direction.iloc[i - 1]
                if direction.iloc[i] == 1 and lower_band.iloc[i] < lower_band.iloc[i - 1]:
                    lower_band.iloc[i] = lower_band.iloc[i - 1]
                if direction.iloc[i] == -1 and upper_band.iloc[i] > upper_band.iloc[i - 1]:
                    upper_band.iloc[i] = upper_band.iloc[i - 1]
            supertrend.iloc[i] = lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
        df["supertrend"] = supertrend
        df["supertrend_direction"] = direction
        return df

    def _calculate_basic_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate basic ATR."""
        high = df["high"]
        low = df["low"]
        close = df["close"]
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)
        return tr.ewm(span=period, adjust=False).mean()

    def get_latest_indicators(self, df: pd.DataFrame) -> Dict:
        """Get the latest indicator values."""
        if df is None or df.empty:
            return {}
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else last
        return {
            "close": last.get("close", 0),
            "open": last.get("open", 0),
            "high": last.get("high", 0),
            "low": last.get("low", 0),
            "volume": last.get("volume", 0),
            "ema_9": last.get("ema_9", 0),
            "ema_20": last.get("ema_20", 0),
            "ema_21": last.get("ema_21", 0),
            "ema_50": last.get("ema_50", 0),
            "ema_200": last.get("ema_200", 0),
            "rsi": last.get("rsi", 50),
            "macd": last.get("macd", 0),
            "macd_signal": last.get("macd_signal", 0),
            "macd_histogram": last.get("macd_histogram", 0),
            "macd_histogram_prev": prev.get("macd_histogram", 0),
            "bb_upper": last.get("bb_upper", 0),
            "bb_middle": last.get("bb_middle", 0),
            "bb_lower": last.get("bb_lower", 0),
            "stoch_k": last.get("stoch_k", 50),
            "stoch_d": last.get("stoch_d", 50),
            "stoch_k_prev": prev.get("stoch_k", 50),
            "stoch_d_prev": prev.get("stoch_d", 50),
            "adx": last.get("adx", 0),
            "plus_di": last.get("plus_di", 0),
            "minus_di": last.get("minus_di", 0),
            "atr": last.get("atr", 0),
            "volume_sma": last.get("volume_sma", 0),
            "volume_ratio": last.get("volume_ratio", 1),
            "supertrend": last.get("supertrend", 0),
            "supertrend_direction": last.get("supertrend_direction", 0),
        }
