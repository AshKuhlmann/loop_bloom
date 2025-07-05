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
    """Return check-ins occurring within the given window.

    Args:
        checkins: All recorded check-ins for the micro-goal.
        window: Number of days to include, counting backwards from today.

    Returns:
        list[Checkin]: Only the check-ins whose ``date`` falls inside the
        specified window.
    """
    # ``window`` is inclusive of today, so a 7-day window looks back 6 days.
    cutoff = date.today() - timedelta(days=window - 1)
    # Return only the check-ins that fall within the calculated window.
    return [ci for ci in checkins if ci.date >= cutoff]


def _current_streak(checkins: List[Checkin]) -> int:
    """Calculate consecutive successes at the end of ``checkins``.

    Args:
        checkins: The full history of check-ins for a micro-goal.

    Returns:
        int: Length of the trailing streak of successful check-ins.
    """
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
    """Determine if ``micro`` should progress to the next stage.

    The evaluation uses either a success ratio or a streak strategy based on
    the user's configuration.

    Args:
        micro: The micro-goal being evaluated.
        window: Optional custom window size in days. When omitted the value is
            read from the micro-goal or global config.
        threshold: Optional ratio required to progress. Falls back to the
            micro-goal's value or the global default when not provided.

    Returns:
        bool: ``True`` when the micro-goal meets the configured progression
        criteria.
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
    """Explain why a micro-goal should or should not progress.

    Args:
        micro: The micro-goal under evaluation.
        window: Optional window override in days.
        threshold: Optional success ratio required to progress.

    Returns:
        list[str]: Human-readable messages describing the evaluation.
    """
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
