"""Notification manager for Telegram, sound, and popup notifications."""

import logging
import asyncio
from datetime import datetime, date
from typing import Optional, Dict
from sqlalchemy.orm import Session
from database.models import NotificationLog, Signal, Trade, User, UserSettings
from utils.sound_player import SoundPlayer
from utils.helpers import format_price, format_percent, format_datetime
from config.constants import SIGNAL_TYPES

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages all notification channels."""

    def __init__(self, session: Session):
        self.session = session
        self.sound_player = SoundPlayer()
        self._telegram_bot = None

    def _get_telegram_config(self) -> Optional[Dict]:
        """Get Telegram configuration from database."""
        user = self.session.query(User).first()
        if user and user.telegram_bot_token and user.telegram_chat_id:
            return {
                "token": user.telegram_bot_token,
                "chat_id": user.telegram_chat_id,
            }
        return None

    def _init_telegram_bot(self):
        """Initialize Telegram bot."""
        config = self._get_telegram_config()
        if config is None:
            return None
        try:
            from telegram import Bot
            return Bot(token=config["token"])
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {e}")
            return None

    def _send_telegram(self, message: str) -> bool:
        """Send message via Telegram."""
        config = self._get_telegram_config()
        if config is None:
            return False
        try:
            from telegram import Bot
            bot = Bot(token=config["token"])
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                bot.send_message(chat_id=config["chat_id"], text=message, parse_mode="HTML")
            )
            loop.close()
            return True
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    def send_signal_notification(self, signal: Dict) -> bool:
        """Send notification for a new signal."""
        settings = self.session.query(UserSettings).first()
        if settings and not settings.notifications_enabled:
            return True

        message = self._format_signal_message(signal)
        sent = self._send_telegram(message)
        self._log_notification(signal.get("id"), message, "telegram", "SENT" if sent else "FAILED")

        if settings and settings.sound_enabled:
            self.sound_player.play_new_signal()

        return sent

    def send_tp_notification(self, signal: Dict, tp_number: int, current_price: float) -> bool:
        """Send TP hit notification."""
        pnl = ((current_price - signal["entry_price"]) / signal["entry_price"]) * 100
        if signal["signal_type"] == "SHORT":
            pnl = -pnl

        emoji = "✅" if tp_number == 1 else "✅✅" if tp_number == 2 else "✅✅✅"
        message = (
            f"{emoji} TP{tp_number} HIT!\n\n"
            f"💹 {signal['symbol']} {signal['signal_type']}\n"
            f"💰 Giriş: {format_price(signal['entry_price'])}\n"
            f"🎯 TP{tp_number}: {format_price(current_price)}\n"
            f"📈 Qazanc: {format_percent(pnl)}\n\n"
            f"Qalan TP-lər aktiv..."
        )
        sent = self._send_telegram(message)
        settings = self.session.query(UserSettings).first()
        if settings and settings.sound_enabled:
            self.sound_player.play_tp_hit()
        return sent

    def send_sl_notification(self, signal: Dict, current_price: float) -> bool:
        """Send SL hit notification."""
        pnl = ((current_price - signal["entry_price"]) / signal["entry_price"]) * 100
        if signal["signal_type"] == "SHORT":
            pnl = -pnl

        message = (
            f"🛑 STOP LOSS HIT!\n\n"
            f"💹 {signal['symbol']} {signal['signal_type']}\n"
            f"💰 Giriş: {format_price(signal['entry_price'])}\n"
            f"🛑 SL: {format_price(current_price)}\n"
            f"📉 Zərər: {format_percent(pnl)}"
        )
        sent = self._send_telegram(message)
        settings = self.session.query(UserSettings).first()
        if settings and settings.sound_enabled:
            self.sound_player.play_sl_hit()
        return sent

    def send_daily_summary(self) -> bool:
        """Send daily summary notification."""
        today = date.today().isoformat()
        signals_today = self.session.query(Signal).filter(
            Signal.created_at.like(f"{today}%")
        ).all()

        total = len(signals_today)
        active = sum(1 for s in signals_today if s.status == "ACTIVE")
        tp_hits = sum(1 for s in signals_today if "TP" in (s.status or ""))
        sl_hits = sum(1 for s in signals_today if s.status == "SL_HIT")
        closed = sum(1 for s in signals_today if s.status == "CLOSED")

        trades_today = self.session.query(Trade).filter(
            Trade.closed_at.like(f"{today}%"),
            Trade.status == "CLOSED"
        ).all()

        daily_pnl = sum(t.pnl_percent or 0 for t in trades_today)
        win_rate = 0
        if trades_today:
            wins = sum(1 for t in trades_today if (t.pnl_percent or 0) > 0)
            win_rate = (wins / len(trades_today)) * 100

        best_trade = ""
        worst_trade = ""
        if trades_today:
            best = max(trades_today, key=lambda t: t.pnl_percent or 0)
            worst = min(trades_today, key=lambda t: t.pnl_percent or 0)
            best_trade = f"{best.symbol} {format_percent(best.pnl_percent)}"
            worst_trade = f"{worst.symbol} {format_percent(worst.pnl_percent)}"

        message = (
            f"📊 GÜNLÜK XÜLASƏ\n\n"
            f"📅 Tarix: {today}\n\n"
            f"📈 Siqnal sayı: {total}\n"
            f"✅ Uğurlu: {tp_hits}\n"
            f"❌ Uğursuz: {sl_hits}\n"
            f"⏳ Aktiv: {active}\n\n"
            f"💰 Günlük PnL: {format_percent(daily_pnl)}\n"
            f"📊 Win Rate: {win_rate:.1f}%\n\n"
        )
        if best_trade:
            message += f"Ən yaxşı: {best_trade}\n"
        if worst_trade:
            message += f"Ən pis: {worst_trade}\n"

        sent = self._send_telegram(message)
        self._log_notification(None, message, "telegram", "SENT" if sent else "FAILED")
        return sent

    def send_test_notification(self) -> bool:
        """Send a test notification."""
        message = (
            "🔔 TEST BİLDİRİŞİ\n\n"
            "Trading Signal System uğurla quruldu!\n"
            f"📅 Vaxt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Bildirişlər aktivdir."
        )
        return self._send_telegram(message)

    def _format_signal_message(self, signal: Dict) -> str:
        """Format signal notification message."""
        signal_emoji = "🟢" if signal["signal_type"] == "LONG" else "🔴"
        market_names = {"crypto": "Kripto", "forex": "Forex", "stocks": "Səhmlər"}
        strategy_names = {
            "scalping": "Scalping", "day_trading": "Day Trading",
            "swing": "Swing Trading", "trend_following": "Trend Following"
        }

        message = (
            f"{signal_emoji} {signal['signal_type']} SİQNAL\n\n"
            f"📊 Bazar: {market_names.get(signal['market'], signal['market'])}\n"
            f"💹 Simvol: {signal['symbol']}\n"
            f"📈 Strategiya: {strategy_names.get(signal['strategy'], signal['strategy'])}\n"
            f"⏱ Timeframe: {signal['timeframe']}\n\n"
            f"💰 Giriş: {format_price(signal['entry_price'])}\n"
            f"🛑 Stop Loss: {format_price(signal['stop_loss'])}\n"
        )

        if signal.get("take_profit_1"):
            rr1 = abs(signal["take_profit_1"] - signal["entry_price"]) / abs(signal["entry_price"] - signal["stop_loss"])
            message += f"✅ TP1: {format_price(signal['take_profit_1'])} (1:{rr1:.1f})\n"
        if signal.get("take_profit_2"):
            rr2 = abs(signal["take_profit_2"] - signal["entry_price"]) / abs(signal["entry_price"] - signal["stop_loss"])
            message += f"✅ TP2: {format_price(signal['take_profit_2'])} (1:{rr2:.1f})\n"
        if signal.get("take_profit_3"):
            rr3 = abs(signal["take_profit_3"] - signal["entry_price"]) / abs(signal["entry_price"] - signal["stop_loss"])
            message += f"✅ TP3: {format_price(signal['take_profit_3'])} (1:{rr3:.1f})\n"

        message += (
            f"\n📊 Risk/Reward: 1:{signal.get('risk_reward_ratio', 0):.1f}\n"
            f"🎯 Confidence: {signal.get('confidence', 'MEDIUM')}\n"
            f"📉 Risk: 1%\n\n"
            f"⏰ Vaxt: {signal.get('created_at', '')[:19]} UTC"
        )
        return message

    def _log_notification(self, signal_id: Optional[int], message: str,
                          channel: str, status: str):
        """Log notification to database."""
        try:
            log = NotificationLog(
                signal_id=signal_id,
                message=message,
                channel=channel,
                status=status,
                sent_at=datetime.utcnow().isoformat()
            )
            self.session.add(log)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error logging notification: {e}")
