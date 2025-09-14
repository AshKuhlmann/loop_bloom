"""Integration test to ensure CSV export includes goal-level micro-habits."""

from __future__ import annotations

import csv
from pathlib import Path

from click.testing import CliRunner

import loopbloom.__main__ as main


def test_export_includes_goal_level_micro(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()

    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))

    # Create goal and a micro directly under the goal (no phase)
    runner.invoke(main.cli, ["goal", "add", "Solo"])  # ignore output
    runner.invoke(main.cli, ["micro", "add", "Alone", "--goal", "Solo"])  # no phase
    runner.invoke(main.cli, ["checkin", "Solo", "--success"])  # one row

    csv_path = tmp_path / "export.csv"
    res = runner.invoke(main.cli, ["export", "--fmt", "csv", "--out", str(csv_path)])
    assert res.exit_code == 0

    rows = list(csv.reader(csv_path.open()))
    assert len(rows) == 2  # header + one check-in
    header = rows[0]
    data = rows[1]
    # phase column should be empty string for goal-level micro
    phase_idx = header.index("phase")
    assert data[phase_idx] == ""
