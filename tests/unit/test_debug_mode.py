from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from loopbloom import __main__ as main
from loopbloom.core.models import GoalArea
from loopbloom.storage.json_store import JSONStore


def test_debug_flag_enables_verbose_logging(tmp_path: Path) -> None:
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(main.cli, ["--debug", "goal", "add", "Logging Goal"], env=env)
    assert res.exit_code == 0
    assert "Debug mode is ON" in res.output


def test_time_override_with_env_var(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    JSONStore(path=Path(env["LOOPBLOOM_DATA_PATH"])).save(
        [GoalArea(name="G", micro_goals=[])]
    )
    monkeypatch.setenv("LOOPBLOOM_DEBUG_DATE", "2025-03-15")
    res = runner.invoke(main.cli, ["--debug", "checkin", "G"], env=env)
    assert res.exit_code == 0
    assert "Check-in recorded for date: 2025-03-15" in res.output


def test_dry_run_prevents_saving(tmp_path: Path) -> None:
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(main.cli, ["--dry-run", "goal", "add", "Dry Goal"], env=env)
    assert res.exit_code == 0
    assert "DRY RUN" in res.output
    data_file = Path(env["LOOPBLOOM_DATA_PATH"])
    assert not data_file.exists() or json.loads(data_file.read_text() or "[]") == []
