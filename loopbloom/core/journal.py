from __future__ import annotations

import json
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder

from loopbloom.core.config import APP_DIR

JOURNAL_PATH = APP_DIR / "journal.json"
JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)


class JournalEntry(BaseModel):
    """Simple journal entry with optional goal tag."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    text: str
    goal: str | None = None


def load_entries() -> List[JournalEntry]:
    """Return all stored journal entries."""
    if not JOURNAL_PATH.exists():
        return []
    with JOURNAL_PATH.open("r", encoding="utf-8") as fp:
        raw = json.load(fp)
    return [JournalEntry.model_validate(obj) for obj in raw]


def add_entry(text: str, goal: str | None = None) -> None:
    """Append a new journal entry to the file."""
    entries = load_entries()
    entries.append(JournalEntry(text=text.strip(), goal=goal))
    with JOURNAL_PATH.open("w", encoding="utf-8") as fp:
        json.dump(entries, fp, default=pydantic_encoder, indent=2)
