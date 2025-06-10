"""Tests for summary CLI helpers."""

from loopbloom.cli.summary import _detail_view, _overview
from loopbloom.core.models import Checkin, GoalArea, MicroGoal, Phase


def test_overview_and_detail(capsys) -> None:
    """Ensure helper functions emit text without error."""
    goal = GoalArea(
        name="G", phases=[Phase(name="P", micro_goals=[MicroGoal(name="M")])]
    )
    goal.phases[0].micro_goals[0].checkins.append(Checkin(success=True))
    _overview([goal])
    out = capsys.readouterr().out
    assert "LoopBloom Progress" in out
    _detail_view("G", [goal])
    out2 = capsys.readouterr().out
    assert "G" in out2
