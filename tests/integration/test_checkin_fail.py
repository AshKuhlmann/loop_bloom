"""Integration test for failed check-in flow."""

from __future__ import annotations

import json

from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_checkin_goal_with_no_active_micro_goals(tmp_path) -> None:
    """Check in when a goal has no active micro-goals."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Setup: create goal and immediately complete its only micro-goal
    runner.invoke(cli, ["goal", "add", "Goal With No Micros"], env=env)
    runner.invoke(
        cli,
        ["micro", "add", "A completed micro", "--goal", "Goal With No Micros"],
        env=env,
    )
    runner.invoke(
        cli,
        ["micro", "complete", "A completed micro", "--goal", "Goal With No Micros"],
        env=env,
    )

    result = runner.invoke(
        cli,
        ["checkin", "Goal With No Micros"],
        env=env,
        input="y\n",
    )

    assert result.exit_code == 0
    assert "No active micro-goal found for this goal." in result.output


def test_failed_checkin(tmp_path) -> None:
    """Add a goal/micro-habit then log a failed check-in."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Setup goal and micro-habit
    runner.invoke(cli, ["goal", "add", "Goal Name"], env=env)
    runner.invoke(
        cli,
        ["micro", "add", "Tiny Habit", "--goal", "Goal Name"],
        env=env,
    )

    res = runner.invoke(cli, ["checkin", "Goal Name", "--fail"], env=env)

    assert res.exit_code == 0
    expected_phrases = ("Skipped", "data, not drama", "No worries")
    assert any(k in res.output for k in expected_phrases)

    data = json.loads((tmp_path / "data.json").read_text())
    assert data[0]["micro_goals"][0]["checkins"][0]["success"] is False
