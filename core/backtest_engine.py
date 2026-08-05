"""Backtest engine for strategy testing."""

import logging
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from core.data_fetcher import DataFetcher
from core.indicator_engine import IndicatorEngine
from core.signal_engine import SignalEngine
from database.models import BacktestResult

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtesting engine for trading strategies."""

    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.indicator_engine = IndicatorEngine()
        self.signal_engine = SignalEngine()

    def run_backtest(self, symbol: str, strategy_name: str, timeframe: str,
                     start_date: str, end_date: str, initial_balance: float = 10000.0) -> Optional[Dict]:
        """Run a backtest for a given symbol and strategy."""
        try:
            df = self.data_fetcher.fetch_ohlcv(symbol, timeframe, self._guess_market(symbol), limit=500)
            if df is None or df.empty:
                logger.warning(f"No data available for backtest: {symbol}")
                return None

            if start_date:
                df = df[df.index >= start_date]
            if end_date:
                df = df[df.index <= end_date]

            df = self.indicator_engine.calculate_all(df)
            if df is None or df.empty:
                return None

            trades = []
            balance = initial_balance
            position = None
            peak_balance = initial_balance
            max_drawdown = 0.0

            for i in range(50, len(df)):
                window = df.iloc[:i + 1]
                current = df.iloc[i]
                current_price = current["close"]

                if position is None:
                    signal = self.signal_engine.generate_signal(
                        window, strategy_name, symbol,
                        self._guess_market(symbol), timeframe
                    )
                    if signal:
                        risk_amount = balance * 0.01
                        risk_per_unit = abs(signal["entry_price"] - signal["stop_loss"])
                        if risk_per_unit > 0:
                            qty = risk_amount / risk_per_unit
                            position = {
                                "type": signal["signal_type"],
                                "entry": signal["entry_price"],
                                "sl": signal["stop_loss"],
                                "tp1": signal.get("take_profit_1"),
                                "qty": qty,
                                "time": str(df.index[i]),
                            }
                else:
                    hit_sl = False
                    hit_tp = False
                    if position["type"] == "LONG":
                        if current["low"] <= position["sl"]:
                            hit_sl = True
                        elif position["tp1"] and current["high"] >= position["tp1"]:
                            hit_tp = True
                    else:
                        if current["high"] >= position["sl"]:
                            hit_sl = True
                        elif position["tp1"] and current["low"] <= position["tp1"]:
                            hit_tp = True

                    if hit_sl:
                        pnl = abs(position["entry"] - position["sl"]) * position["qty"]
                        if position["type"] == "LONG":
                            pnl = -pnl
                        balance += pnl
                        trades.append({
                            "entry": position["entry"],
                            "exit": position["sl"],
                            "type": position["type"],
                            "pnl": pnl,
                            "result": "LOSS",
                            "entry_time": position["time"],
                            "exit_time": str(df.index[i]),
                        })
                        position = None
                    elif hit_tp:
                        pnl = abs(position["tp1"] - position["entry"]) * position["qty"]
                        balance += pnl
                        trades.append({
                            "entry": position["entry"],
                            "exit": position["tp1"],
                            "type": position["type"],
                            "pnl": pnl,
                            "result": "WIN",
                            "entry_time": position["time"],
                            "exit_time": str(df.index[i]),
                        })
                        position = None

                peak_balance = max(peak_balance, balance)
                drawdown = (peak_balance - balance) / peak_balance * 100
                max_drawdown = max(max_drawdown, drawdown)

            if position:
                final_price = df.iloc[-1]["close"]
                if position["type"] == "LONG":
                    pnl = (final_price - position["entry"]) * position["qty"]
                else:
                    pnl = (position["entry"] - final_price) * position["qty"]
                balance += pnl
                trades.append({
                    "entry": position["entry"],
                    "exit": final_price,
                    "type": position["type"],
                    "pnl": pnl,
                    "result": "WIN" if pnl > 0 else "LOSS",
                    "entry_time": position["time"],
                    "exit_time": str(df.index[-1]),
                })

            winning = [t for t in trades if t["result"] == "WIN"]
            losing = [t for t in trades if t["result"] == "LOSS"]
            total_pnl = sum(t["pnl"] for t in trades)
            total_pnl_percent = ((balance - initial_balance) / initial_balance) * 100
            win_rate = (len(winning) / len(trades) * 100) if trades else 0
            gross_profit = sum(t["pnl"] for t in winning)
            gross_loss = abs(sum(t["pnl"] for t in losing))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
            returns = pd.Series([t["pnl"] / initial_balance for t in trades])
            sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0

            result = {
                "strategy": strategy_name,
                "symbol": symbol,
                "timeframe": timeframe,
                "start_date": start_date or str(df.index[0]),
                "end_date": end_date or str(df.index[-1]),
                "total_trades": len(trades),
                "winning_trades": len(winning),
                "losing_trades": len(losing),
                "win_rate": round(win_rate, 2),
                "profit_factor": round(profit_factor, 2),
                "max_drawdown": round(max_drawdown, 2),
                "total_pnl_percent": round(total_pnl_percent, 2),
                "sharpe_ratio": round(sharpe, 2),
                "trades": trades,
                "equity_curve": self._build_equity_curve(trades, initial_balance),
            }
            return result
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return None

    def _build_equity_curve(self, trades: List[Dict], initial: float) -> List[float]:
        """Build equity curve from trades."""
        curve = [initial]
        balance = initial
        for t in trades:
            balance += t["pnl"]
            curve.append(round(balance, 2))
        return curve

    def _guess_market(self, symbol: str) -> str:
        """Guess market from symbol name."""
        if symbol.endswith("USDT") or symbol.endswith("BTC") or symbol.endswith("ETH"):
            return "crypto"
        if len(symbol) == 6 and symbol.isalpha():
            return "forex"
        return "stocks"

    def save_result(self, session, result: Dict):
        """Save backtest result to database."""
        try:
            bt = BacktestResult(
                strategy=result["strategy"],
                symbol=result["symbol"],
                timeframe=result["timeframe"],
                start_date=result["start_date"],
                end_date=result["end_date"],
                total_trades=result["total_trades"],
                winning_trades=result["winning_trades"],
                losing_trades=result["losing_trades"],
                win_rate=result["win_rate"],
                profit_factor=result["profit_factor"],
                max_drawdown=result["max_drawdown"],
                total_pnl_percent=result["total_pnl_percent"],
                sharpe_ratio=result["sharpe_ratio"],
            )
            session.add(bt)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving backtest result: {e}")
