import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from loopbloom.core.config import APP_DIR


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with a rotating file handler.

    Args:
        level: Logging level used for the root logger. Defaults to ``INFO``.
    """
    # Prefer file logging, but fall back to stderr when the config directory
    # is not writable (e.g. in sandboxed environments).
    handler: logging.Handler
    log_file: Path | None = None
    try:
        log_dir = APP_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "loopbloom.log"
        handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    except Exception:
        handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    # Avoid adding duplicate handlers if called multiple times
    def _same_handler(h: logging.Handler) -> bool:
        if (
            isinstance(handler, RotatingFileHandler)
            and isinstance(h, RotatingFileHandler)
            and log_file is not None
        ):
            return Path(h.baseFilename) == log_file
        return type(h) is type(handler)

    if not any(_same_handler(h) for h in root_logger.handlers):
        root_logger.addHandler(handler)
    root_logger.setLevel(level)
