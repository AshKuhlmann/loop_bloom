"""Pep-talk template library + weighted random selector.

Short motivational messages are stored in a JSON file and loaded lazily on
first use.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List

# Directory containing bundled data files such as the default pep talks.
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# JSON file with two lists of pep-talk snippets keyed by mood (success/skip).
TALKS_PATH = DATA_DIR / "default_talks.json"


class TalkPool:
    """Loads pep-talk templates grouped by key (success | skip)."""

    _cache: Dict[str, List[str]] | None = None

    @classmethod
    def _load(cls) -> Dict[str, List[str]]:
        # Lazily read and parse the bundled pep talk file only once per run.
        # Caching avoids unnecessary disk I/O when multiple pep talks are
        # requested in a single invocation.
        if cls._cache is None:
            cls._cache = json.loads(TALKS_PATH.read_text())
        return cls._cache

    @classmethod
    def random(cls, mood: str = "success") -> str:  # mood: success | skip
        """Return a random pep talk for the given ``mood``."""
        # Retrieve the list for the requested mood, falling back to an
        # empty list if the mood doesn't exist in the JSON file.
        pool = cls._load().get(mood, [])
        if not pool:
            # Default message when no templates are available.
            return "Great job!"
        # ``random.choice`` provides an even distribution across messages.
        return random.choice(pool)
