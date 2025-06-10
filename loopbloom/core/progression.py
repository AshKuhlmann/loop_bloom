"""Automatic progression rule.

If an active micro-habit hits ≥ `threshold` success ratio within the last `window` days,
`should_advance()` returns True.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from loopbloom.core.models import Checkin, MicroGoal

WINDOW_DEFAULT = 14  # days
THRESHOLD_DEFAULT = 0.80  # 80 %


def _recent_checkins(checkins: List[Checkin], window: int) -> List[Checkin]:
    cutoff = date.today() - timedelta(days=window - 1)
    return [ci for ci in checkins if ci.date >= cutoff]


def should_advance(
    micro: MicroGoal,
    *,
    window: int = WINDOW_DEFAULT,
    threshold: float = THRESHOLD_DEFAULT,
) -> bool:
    """Return True if micro-habit qualifies for advancement."""
    recent = _recent_checkins(micro.checkins, window)
    if len(recent) < window:  # need full window
        return False
    success_ratio = sum(ci.success for ci in recent) / window
    return success_ratio >= threshold
