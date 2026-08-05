"""Sound player utility for notifications."""

import logging
import os
import platform
from pathlib import Path

logger = logging.getLogger(__name__)


class SoundPlayer:
    """Plays notification sounds."""

    def __init__(self):
        self.enabled = True
        self.sounds_dir = Path(__file__).parent.parent / "resources" / "sounds"
        self._ensure_sounds_exist()

    def _ensure_sounds_exist(self):
        """Create placeholder sound files if they don't exist."""
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
        sound_files = ["new_signal.wav", "tp_hit.wav", "sl_hit.wav", "notification.wav"]
        for sound_file in sound_files:
            sound_path = self.sounds_dir / sound_file
            if not sound_path.exists():
                try:
                    self._create_wav_placeholder(str(sound_path))
                except Exception as e:
                    logger.warning(f"Could not create sound file {sound_file}: {e}")

    def _create_wav_placeholder(self, filepath: str):
        """Create a minimal valid WAV file."""
        import struct
        sample_rate = 22050
        duration = 0.2
        num_samples = int(sample_rate * duration)
        data = b""
        for i in range(num_samples):
            value = int(16000 * (i / num_samples) * (1 if i % 2 == 0 else -1))
            data += struct.pack("<h", max(-32768, min(32767, value)))

        with open(filepath, "wb") as f:
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + len(data)))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write(struct.pack("<I", 16))
            f.write(struct.pack("<HHIIHH", 1, 1, sample_rate, sample_rate * 2, 2, 16))
            f.write(b"data")
            f.write(struct.pack("<I", len(data)))
            f.write(data)

    def play(self, sound_name: str):
        """Play a sound file by name."""
        if not self.enabled:
            return
        sound_path = self.sounds_dir / sound_name
        if not sound_path.exists():
            logger.warning(f"Sound file not found: {sound_name}")
            return
        try:
            system = platform.system()
            if system == "Windows":
                os.system(f'start /min "" "powershell" -c "(New-Object Media.SoundPlayer \'{sound_path}\').PlaySync()"')
            elif system == "Darwin":
                os.system(f"afplay '{sound_path}' &")
            else:
                os.system(f"aplay '{sound_path}' &")
        except Exception as e:
            logger.error(f"Error playing sound {sound_name}: {e}")

    def play_new_signal(self):
        """Play new signal notification sound."""
        self.play("new_signal.wav")

    def play_tp_hit(self):
        """Play take profit hit sound."""
        self.play("tp_hit.wav")

    def play_sl_hit(self):
        """Play stop loss hit sound."""
        self.play("sl_hit.wav")

    def play_notification(self):
        """Play general notification sound."""
        self.play("notification.wav")

    def set_enabled(self, enabled: bool):
        """Enable or disable sounds."""
        self.enabled = enabled
