"""Automatic progression rule.

If an active micro-habit hits ≥ `threshold` success ratio within the last
`window` days, ``should_advance()`` returns ``True``.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from loopbloom.constants import THRESHOLD_DEFAULT, WINDOW_DEFAULT
from loopbloom.core import config as cfg
from loopbloom.core.config import ProgressionStrategy
from loopbloom.core.models import Checkin, MicroGoal


def _recent_checkins(checkins: List[Checkin], window: int) -> List[Checkin]:
    """Return check-ins occurring within the last ``window`` days."""
    # ``window`` is inclusive of today, so a 7-day window looks back 6 days.
    cutoff = date.today() - timedelta(days=window - 1)
    # Return only the check-ins that fall within the calculated window.
    return [ci for ci in checkins if ci.date >= cutoff]


def _current_streak(checkins: List[Checkin]) -> int:
    """Return trailing run of successful check-ins."""
    streak = 0
    ordered = sorted(checkins, key=lambda c: c.date)
    for ci in reversed(ordered):
        if ci.success:
            streak += 1
        else:
            break
    return streak


def should_advance(
    micro: MicroGoal,
    *,
    window: int | None = None,
    threshold: float | None = None,
) -> bool:
    """Return True if micro-habit qualifies for advancement.

    If ``window`` or ``threshold`` are omitted, values are looked up on the
    ``micro`` object first (``advancement_window`` and
    ``advancement_threshold``). When those aren't defined, global
    defaults from :mod:`loopbloom.core.config` are used (keys
    ``advance.window`` and ``advance.threshold``).
    """
    # ``window`` and ``threshold`` may be specified per micro-habit or fall
    # back to the user configuration.
    if window is None:
        window = micro.advancement_window
    if threshold is None:
        threshold = micro.advancement_threshold
    conf = cfg.load().get("advance", {})
    strategy = ProgressionStrategy(conf.get("strategy", "ratio"))
    if window is None or threshold is None:
        if window is None:
            window = int(conf.get("window", WINDOW_DEFAULT))
        if threshold is None:
            threshold = float(conf.get("threshold", THRESHOLD_DEFAULT))

    if strategy is ProgressionStrategy.STREAK:
        streak_target = int(conf.get("streak_to_advance", 10))
        return _current_streak(micro.checkins) >= streak_target

    recent = _recent_checkins(micro.checkins, window)
    if len(recent) < window:
        return False
    success_ratio = sum(ci.success for ci in recent) / window
    return success_ratio >= threshold


def get_progression_reasons(
    micro: MicroGoal,
    *,
    window: int | None = None,
    threshold: float | None = None,
) -> list[str]:
    """Return reasons explaining the progression decision."""
    if window is None:
        window = micro.advancement_window
    if threshold is None:
        threshold = micro.advancement_threshold
    conf = cfg.load().get("advance", {})
    strategy = ProgressionStrategy(conf.get("strategy", "ratio"))
    if window is None or threshold is None:
        if window is None:
            window = int(conf.get("window", WINDOW_DEFAULT))
        if threshold is None:
            threshold = float(conf.get("threshold", THRESHOLD_DEFAULT))

    reasons: list[str] = []
    if strategy is ProgressionStrategy.STREAK:
        streak_target = int(conf.get("streak_to_advance", 10))
        streak = _current_streak(micro.checkins)
        reasons.append(f"Current streak {streak}/{streak_target}")
        return reasons

    recent = _recent_checkins(micro.checkins, window)
    successes = sum(ci.success for ci in recent)
    reasons.append(f"{successes} successes in last {len(recent)}/{window} days")
    if len(recent) < window:
        remaining = window - len(recent)
        reasons.append(f"{remaining} more day(s) needed for full window")
    ratio = successes / window if window else 0
    reasons.append(f"Success rate {ratio:.0%} (threshold {threshold:.0%})")
    return reasons
