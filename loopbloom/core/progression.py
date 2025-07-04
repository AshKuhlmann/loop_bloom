"""Automatic progression rule.

If an active micro-habit hits ≥ `threshold` success ratio within the last
`window` days, ``should_advance()`` returns ``True``.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

from loopbloom.core import config as cfg
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
    if window is None or threshold is None:
        # Pull defaults from the user's config so behaviour can be tuned
        # without modifying library code.
        conf = cfg.load().get("advance", {})
        if window is None:
            window = int(conf.get("window", WINDOW_DEFAULT))
        if threshold is None:
            threshold = float(conf.get("threshold", THRESHOLD_DEFAULT))

    # Filter check-ins down to just those within the relevant window.
    recent = _recent_checkins(micro.checkins, window)
    if len(recent) < window:  # need full window
        # Not enough data yet to make a decision.
        return False
    success_ratio = sum(ci.success for ci in recent) / window
    # True when the user's streak meets or exceeds the threshold.
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
    if window is None or threshold is None:
        conf = cfg.load().get("advance", {})
        if window is None:
            window = int(conf.get("window", WINDOW_DEFAULT))
        if threshold is None:
            threshold = float(conf.get("threshold", THRESHOLD_DEFAULT))

    recent = _recent_checkins(micro.checkins, window)
    successes = sum(ci.success for ci in recent)
    reasons: list[str] = []
    reasons.append(f"{successes} successes in last {len(recent)}/{window} days")
    if len(recent) < window:
        remaining = window - len(recent)
        reasons.append(f"{remaining} more day(s) needed for full window")
    ratio = successes / window if window else 0
    reasons.append(f"Success rate {ratio:.0%} (threshold {threshold:.0%})")
    return reasons
