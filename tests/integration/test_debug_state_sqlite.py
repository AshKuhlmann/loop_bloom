"""Integration test for `debug-state` with SQLite backend."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

import loopbloom.__main__ as main


def test_debug_state_sqlite_dump(tmp_path: Path, monkeypatch) -> None:
    runner = CliRunner()
    # Isolate config under tmp and force a .db data path
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    db_path = tmp_path / "data.db"
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(db_path))

    # Create some data in SQLite (extension enforces sqlite backend)
    res = runner.invoke(main.cli, ["goal", "add", "X"])
    assert res.exit_code == 0

    # Dump state; should be valid JSON listing goals
    res = runner.invoke(main.cli, ["debug-state"])
    assert res.exit_code == 0
    # Output is pretty JSON; verify it parses and contains our goal
    data = json.loads(res.stdout)
    assert isinstance(data, list)
    assert any(g.get("name") == "X" for g in data)
