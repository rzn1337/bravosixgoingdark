from __future__ import annotations

import logging
import sys

_LOGGER_NAME = "humansim"


def setup_logging(level: str = "INFO", logfile: str | None = None) -> logging.Logger:
    """Configure and return the package logger. Idempotent."""
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level.upper())
    # Avoid duplicate handlers if called twice.
    if not any(getattr(h, "_humansim", False) for h in logger.handlers):
        fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", "%H:%M:%S")
        ch = logging.StreamHandler(sys.stderr)
        ch.setFormatter(fmt)
        ch._humansim = True  # type: ignore[attr-defined]
        logger.addHandler(ch)
        if logfile:
            fh = logging.FileHandler(logfile, encoding="utf-8")
            fh.setFormatter(fmt)
            fh._humansim = True  # type: ignore[attr-defined]
            logger.addHandler(fh)
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(_LOGGER_NAME)
