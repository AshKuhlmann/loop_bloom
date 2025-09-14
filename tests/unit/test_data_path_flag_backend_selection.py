"""Ensure --data-path flag enforces backend by extension."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

from click.testing import CliRunner


def _reload_cli(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import loopbloom.__main__ as main
    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    importlib.reload(main)
    return main.cli


def test_flag_json_forces_json_backend(tmp_path: Path, monkeypatch) -> None:
    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    data_path = tmp_path / "flag.json"
    res = runner.invoke(cli, ["--data-path", str(data_path), "goal", "add", "X"])
    assert res.exit_code == 0
    loaded = json.loads(data_path.read_text())
    assert isinstance(loaded, list)


def test_flag_db_forces_sqlite_backend(tmp_path: Path, monkeypatch) -> None:
    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    data_path = tmp_path / "flag.db"
    res = runner.invoke(cli, ["--data-path", str(data_path), "goal", "add", "Y"])
    assert res.exit_code == 0
    sig = data_path.read_bytes()[:15]
    assert sig == b"SQLite format 3"
