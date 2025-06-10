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
