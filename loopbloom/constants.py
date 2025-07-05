from __future__ import annotations

import os
from pathlib import Path

from loopbloom.core.config import APP_DIR

# Base package directory
PACKAGE_DIR = Path(__file__).resolve().parent

# Bundled data directory and resources
DATA_DIR = PACKAGE_DIR / "data"
COPING_DIR = DATA_DIR / "coping"
TALKS_PATH = DATA_DIR / "default_talks.json"

# User data files
REVIEW_PATH = APP_DIR / "reviews.json"
REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)

JOURNAL_PATH = APP_DIR / "journal.json"
JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)

JSON_STORE_PATH = Path(os.getenv("LOOPBLOOM_DATA_PATH", APP_DIR / "data.json"))
JSON_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

SQLITE_STORE_PATH = Path(os.getenv("LOOPBLOOM_SQLITE_PATH", APP_DIR / "data.db"))
SQLITE_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Progression and reporting defaults
WINDOW_DEFAULT = 14
THRESHOLD_DEFAULT = 0.80
DEFAULT_TIMEFRAME = 30
