from __future__ import annotations

import json
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder

from loopbloom.constants import JOURNAL_PATH


class JournalEntry(BaseModel):
    """Simple journal entry with optional goal tag."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    text: str
    goal: str | None = None


def load_entries() -> List[JournalEntry]:
    """Load all stored journal entries from disk.

    Returns:
        list[JournalEntry]: Chronologically ordered journal entries.
    """
    if not JOURNAL_PATH.exists():
        return []
    with JOURNAL_PATH.open("r", encoding="utf-8") as fp:
        raw = json.load(fp)
    return [JournalEntry.model_validate(obj) for obj in raw]


def add_entry(text: str, goal: str | None = None) -> None:
    """Append a new journal entry to the journal file.

    Args:
        text: Entry text supplied by the user.
        goal: Optional goal name associated with the entry.
    """
    entries = load_entries()
    entries.append(JournalEntry(text=text.strip(), goal=goal))
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with JOURNAL_PATH.open("w", encoding="utf-8") as fp:
        json.dump(entries, fp, default=pydantic_encoder, indent=2)
