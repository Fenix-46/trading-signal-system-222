"""Application settings manager."""

import os
import json
from pathlib import Path


class AppSettings:
    """Manages application settings and paths."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.app_name = "TradingSignalSystem"
        self.base_dir = self._get_base_dir()
        self.data_dir = self.base_dir
        self.db_path = self.data_dir / "trading_signals.db"
        self.log_path = self.data_dir / "app.log"
        self.config_path = self.data_dir / "config.json"
        self.resources_dir = Path(__file__).parent.parent / "resources"
        self.sounds_dir = self.resources_dir / "sounds"
        self.images_dir = self.resources_dir / "images"
        self._ensure_dirs()

    def _get_base_dir(self) -> Path:
        """Get the base directory for app data."""
        if os.name == "nt":
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        else:
            base = Path.home() / ".config"
        return base / self.app_name

    def _ensure_dirs(self):
        """Ensure all required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sounds_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> dict:
        """Load configuration from JSON file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_config(self, config: dict):
        """Save configuration to JSON file."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Config save error: {e}")

    def get_resource_path(self, filename: str) -> str:
        """Get full path for a resource file."""
        return str(self.resources_dir / filename)

    def get_sound_path(self, filename: str) -> str:
        """Get full path for a sound file."""
        return str(self.sounds_dir / filename)

    def get_image_path(self, filename: str) -> str:
        """Get full path for an image file."""
        return str(self.images_dir / filename)
