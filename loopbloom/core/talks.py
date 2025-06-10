"""Pep-talk template library + weighted random selector."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List

TALKS_PATH = Path(__file__).resolve().parent.parent / "data" / "default_talks.json"


class TalkPool:
    """Loads pep-talk templates grouped by key (success | skip)."""

    _cache: Dict[str, List[str]] | None = None

    @classmethod
    def _load(cls) -> Dict[str, List[str]]:
        if cls._cache is None:
            cls._cache = json.loads(TALKS_PATH.read_text())
        return cls._cache

    @classmethod
    def random(cls, mood: str = "success") -> str:  # mood: success | skip
        """Return a random pep talk for the given ``mood``."""
        pool = cls._load().get(mood, [])
        if not pool:
            return "Great job!"
        return random.choice(pool)
