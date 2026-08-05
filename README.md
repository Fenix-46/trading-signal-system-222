# Trading Signal System

Universal Trading Siqnal Sistemi - Kripto, Forex və Səhmlər bazarları üçün avtomatik siqnal generasiya sistemi.

## Xüsusiyyətlər

- 3 bazar: Kripto, Forex, Səhmlər
- 4 strategiya: Scalping, Day Trading, Swing Trading, Trend Following
- Avtomatik siqnal generasiya
- Telegram bildirişləri
- Avtomatik trade (simulyasiya)
- Backtest sistemi
- Dark theme UI
- System tray dəstəyi

## Quraşdırma

### Requirement-ların quraşdırılması:

```bash
pip install -r requirements.txt
```

### Proqramın işə salınması:

```bash
python main.py
```

### EXE yaratmaq:

```bash
python build.py
```

## Telegram Bot Quraşdırması

1. Telegram-da @BotFather-a yazın
2. `/newbot` komandasını göndərin
3. Bot adını daxil edin
4. Bot Token-i kopyalayın
5. @userinfobot-a yazın və Chat ID-ni öyrənin
6. Proqramda Settings > Telegram bölməsinə token və Chat ID daxil edin
7. "Test Bildiriş Göndər" düyməsi ilə yoxlayın

## Strategiyalar

### Scalping
- Timeframe: 1m, 5m
- Qısa müddətli trades
- Sürətli giriş/çıxış

### Day Trading
- Timeframe: 15m, 1h
- Gündəlik trades
- Eyni gün bağlanır

### Swing Trading
- Timeframe: 4h, 1D
- Orta müddətli trades
- Bir neçə gün açıq qalır

### Trend Following
- Timeframe: 4h, 1D
- Trend istiqamətində trades
- Uzun müddətli pozisiyalar

## Tez-tez Verilən Suallar

### Proqram işləmir?
- Python 3.11+ quraşdırıldığından əmin olun
- `pip install -r requirements.txt` icra edin

### Telegram bildirişləri gəlmir?
- Bot Token və Chat ID-ni yoxlayın
- Botu qrupa əlavə edin və ya private chat-da mesaj göndərin

### Backtest nəticəsi boşdur?
- Seçilmiş simvol üçün data mövcud ola bilər
- Fərqli timeframe və ya strategiya sınayın

## Lisenziya

MIT License
