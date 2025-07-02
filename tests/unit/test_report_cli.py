"""Tests for report CLI helpers."""

from datetime import date

from loopbloom.cli.report import (
    _calendar_heatmap,
    _line_chart,
    _success_bars,
)
from loopbloom.core.models import Checkin, GoalArea, MicroGoal


def test_report_helpers(capsys) -> None:  # noqa: D103
    goal = GoalArea(name="G", micro_goals=[MicroGoal(name="M")])
    goal.micro_goals[0].checkins.append(
        Checkin(date=date.today(), success=True)
    )
    _calendar_heatmap([goal])
    out = capsys.readouterr().out
    assert "LoopBloom Check-in Heatmap" in out
    _success_bars([goal])
    out2 = capsys.readouterr().out
    assert "Success Rates per Goal" in out2
    _line_chart([goal])
    out3 = capsys.readouterr().out
    assert "Success Rate" in out3
