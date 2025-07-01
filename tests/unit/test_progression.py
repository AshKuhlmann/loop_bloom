"""Unit tests for progression rule."""

from datetime import date, timedelta

import pytest

from loopbloom.core.models import Checkin, MicroGoal
from loopbloom.core.progression import should_advance

TODAY = date.today()


@pytest.mark.parametrize(
    "successes,total,expected",
    [
        (12, 14, True),  # 85 %
        (11, 14, False),  # 78 %
        (14, 13, False),  # total<window ⇒ False
    ],
)
def test_should_advance_edge_cases(successes, total, expected):
    """Verify edge cases for should_advance()."""
    mg = MicroGoal(name="Test")
    for i in range(total):
        day = TODAY - timedelta(days=i)
        mg.checkins.append(Checkin(date=day, success=i < successes))
    assert should_advance(mg) is expected


def test_should_advance_respects_config(monkeypatch) -> None:
    """Changing config alters advancement logic."""
    mg = MicroGoal(name="Cfg")
    mg.checkins.append(Checkin(date=TODAY, success=True))
    mg.checkins.append(Checkin(date=TODAY - timedelta(days=1), success=False))
    monkeypatch.setattr(
        "loopbloom.core.config.load",
        lambda: {"advance": {"threshold": 0.5, "window": 2}},
    )
    assert should_advance(mg)


def test_microgoal_custom_criteria(monkeypatch) -> None:
    """Per-micro-goal settings override global config."""
    mg = MicroGoal(
        name="Custom",
        advancement_window=3,
        advancement_threshold=0.6,
    )
    for i in range(3):
        day = TODAY - timedelta(days=i)
        mg.checkins.append(Checkin(date=day, success=i != 1))
    # Global config would fail this streak, but custom criteria should pass.
    monkeypatch.setattr(
        "loopbloom.core.config.load",
        lambda: {"advance": {"threshold": 0.99, "window": 14}},
    )
    assert should_advance(mg)
