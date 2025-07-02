"""Integration test for skipped check-in flow."""

from __future__ import annotations

import json

from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_skipped_checkin(tmp_path) -> None:
    """Add a goal/micro-habit then log a skipped check-in."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Setup goal and micro-habit
    runner.invoke(cli, ["goal", "add", "Goal Name"], env=env)
    runner.invoke(
        cli,
        ["micro", "add", "Tiny Habit", "--goal", "Goal Name"],
        env=env,
    )

    res = runner.invoke(cli, ["checkin", "Goal Name", "--skip"], env=env)

    assert res.exit_code == 0
    expected_phrases = ("Skipped", "data, not drama", "No worries")
    assert any(k in res.output for k in expected_phrases)

    data = json.loads((tmp_path / "data.json").read_text())
    assert data[0]["micro_goals"][0]["checkins"][0]["success"] is False
