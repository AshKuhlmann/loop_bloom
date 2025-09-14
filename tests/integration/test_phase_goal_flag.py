"""Integration tests for `goal phase` with --goal flag support."""

from __future__ import annotations

from click.testing import CliRunner

import loopbloom.__main__ as main


def test_phase_add_rm_with_goal_flag(tmp_path, monkeypatch) -> None:
    runner = CliRunner()

    # Isolate data path for this test
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))

    # Create goal
    res = runner.invoke(main.cli, ["goal", "add", "Sleep"])
    assert res.exit_code == 0

    # Add phase via original positional form (still supported)
    res = runner.invoke(main.cli, ["goal", "phase", "add", "Sleep", "Base"])
    assert res.exit_code == 0
    assert "Added phase 'Base' to Sleep" in res.output

    # Remove phase using the --goal flag (new supported flag)
    res = runner.invoke(
        main.cli, ["goal", "phase", "rm", "Sleep", "Base", "--goal", "Sleep", "--yes"]
    )
    assert res.exit_code == 0
    assert "Deleted phase 'Base' from Sleep" in res.output
