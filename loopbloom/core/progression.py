"""Automatic progression rule.

If an active micro-habit hits ≥ `threshold` success ratio within the last
`window` days, ``should_advance()`` returns ``True``.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from loopbloom.core import config as cfg
from loopbloom.core.config import ProgressionStrategy
from loopbloom.core.models import Checkin, MicroGoal

# Default history window and success rate threshold for progression logic.
WINDOW_DEFAULT = 14  # days to consider
THRESHOLD_DEFAULT = 0.80  # 80 % success required


def _recent_checkins(checkins: List[Checkin], window: int) -> List[Checkin]:
    """Return check-ins occurring within the last ``window`` days."""
    # ``window`` is inclusive of today, so a 7-day window looks back 6 days.
    cutoff = date.today() - timedelta(days=window - 1)
    # Return only the check-ins that fall within the calculated window.
    return [ci for ci in checkins if ci.date >= cutoff]


def _current_streak(checkins: List[Checkin]) -> int:
    """Return length of the current success streak."""
    if not checkins:
        return 0
    ordered = sorted(checkins, key=lambda c: c.date, reverse=True)
    streak = 0
    last_date: date | None = None
    for ci in ordered:
        if last_date is not None and (last_date - ci.date).days > 1:
            break
        if not ci.success:
            break
        streak += 1
        last_date = ci.date
    return streak


def should_advance(
    micro: MicroGoal,
    *,
    window: int | None = None,
    threshold: float | None = None,
    strategy: ProgressionStrategy | None = None,
    streak_to_advance: int | None = None,
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
    if (
        window is None
        or threshold is None
        or strategy is None
        or (
            strategy == ProgressionStrategy.STREAK
            and streak_to_advance is None
        )
    ):
        # Pull defaults from the user's config so behaviour can be tuned
        # without modifying library code.
        conf = cfg.load().get("advance", {})
        if window is None:
            window = int(conf.get("window", WINDOW_DEFAULT))
        if threshold is None:
            threshold = float(conf.get("threshold", THRESHOLD_DEFAULT))
        if strategy is None:
            strategy = ProgressionStrategy(conf.get("strategy", "ratio"))
        if streak_to_advance is None:
            streak_to_advance = int(conf.get("streak_to_advance", 10))

    if strategy == ProgressionStrategy.STREAK:
        streak = _current_streak(micro.checkins)
        assert streak_to_advance is not None
        return streak >= streak_to_advance

    # Ratio strategy
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
    strategy: ProgressionStrategy | None = None,
    streak_to_advance: int | None = None,
) -> list[str]:
    """Return reasons explaining the progression decision."""
    if window is None:
        window = micro.advancement_window
    if threshold is None:
        threshold = micro.advancement_threshold
    if (
        window is None
        or threshold is None
        or strategy is None
        or (
            strategy == ProgressionStrategy.STREAK
            and streak_to_advance is None
        )
    ):
        conf = cfg.load().get("advance", {})
        if window is None:
            window = int(conf.get("window", WINDOW_DEFAULT))
        if threshold is None:
            threshold = float(conf.get("threshold", THRESHOLD_DEFAULT))
        if strategy is None:
            strategy = ProgressionStrategy(conf.get("strategy", "ratio"))
        if streak_to_advance is None:
            streak_to_advance = int(conf.get("streak_to_advance", 10))

    reasons: list[str] = []

    if strategy == ProgressionStrategy.STREAK:
        streak = _current_streak(micro.checkins)
        reasons.append(f"Current streak: {streak}/{streak_to_advance}")
        return reasons

    recent = _recent_checkins(micro.checkins, window)
    successes = sum(ci.success for ci in recent)
    reasons.append(
        f"{successes} successes in last {len(recent)}/{window} days"
    )
    if len(recent) < window:
        remaining = window - len(recent)
        reasons.append(f"{remaining} more day(s) needed for full window")
    ratio = successes / window if window else 0
    reasons.append(f"Success rate {ratio:.0%} (threshold {threshold:.0%})")
    return reasons
