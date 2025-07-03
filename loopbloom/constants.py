"""Central location for application-wide default values."""

from __future__ import annotations

import os
from pathlib import Path

from loopbloom.core.config import APP_DIR

# Numeric defaults used across commands and services
WINDOW_DEFAULT = 14  # days considered when summarising progress
THRESHOLD_DEFAULT = 0.80  # 80 % success required for advancement
DEFAULT_TIMEFRAME = 30  # days displayed in report line charts

# Default storage locations
JSON_DEFAULT_PATH = Path(os.getenv("LOOPBLOOM_DATA_PATH", APP_DIR / "data.json"))
JSON_DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)

SQLITE_DEFAULT_PATH = Path(os.getenv("LOOPBLOOM_SQLITE_PATH", APP_DIR / "data.db"))
SQLITE_DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Journal and review file paths
JOURNAL_PATH = APP_DIR / "journal.json"
JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)

REVIEW_PATH = APP_DIR / "reviews.json"
REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)

# Bundled data directory and assets
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TALKS_PATH = DATA_DIR / "default_talks.json"
COPING_DIR = DATA_DIR / "coping"

# Generic fallback pep talk when no templates are available
PEP_TALK_FALLBACK = "Great job!"
