"""Logging configuration."""

import logging
import sys
from pathlib import Path
from config.settings import AppSettings


def setup_logger(name: str = "trading_system", level: int = logging.INFO) -> logging.Logger:
    """Set up and configure application logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    settings = AppSettings()
    try:
        file_handler = logging.FileHandler(
            str(settings.log_path), encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
