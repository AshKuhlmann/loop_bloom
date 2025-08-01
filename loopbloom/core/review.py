from __future__ import annotations

import json
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from pydantic.json import pydantic_encoder

from loopbloom.constants import REVIEW_PATH


class ReviewEntry(BaseModel):
    """Reflection entry for a given period."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    period: str
    went_well: str


def load_entries() -> List[ReviewEntry]:
    """Load saved reflection entries from disk."""
    if not REVIEW_PATH.exists():
        return []
    with REVIEW_PATH.open("r", encoding="utf-8") as fp:
        raw = json.load(fp)
    return [ReviewEntry.model_validate(obj) for obj in raw]


def add_entry(period: str, went_well: str) -> None:
    """Persist a new review entry.

    Args:
        period: Period covered by the reflection.
        went_well: Summary of what went well during that period.
    """
    entries = load_entries()
    entries.append(ReviewEntry(period=period, went_well=went_well.strip()))
    with REVIEW_PATH.open("w", encoding="utf-8") as fp:
        json.dump(entries, fp, default=pydantic_encoder, indent=2)
