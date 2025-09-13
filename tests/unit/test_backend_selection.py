"""Tests for backend selection based on data path extension.

These tests ensure that when ``LOOPBLOOM_DATA_PATH`` is set, the CLI picks
the appropriate storage backend by inspecting the file extension, regardless
of what the saved config contains.
"""

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


def test_ext_json_forces_json_backend(tmp_path: Path, monkeypatch) -> None:
    """.json path uses JSON backend even if config says sqlite."""
    cli = _reload_cli(tmp_path, monkeypatch)
    # Write a config that would normally select sqlite.
    import loopbloom.core.config as cfg

    cfg.save({"storage": "sqlite"})
    data_path = tmp_path / "data.json"
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(data_path))

    runner = CliRunner()
    res = runner.invoke(cli, ["goal", "add", "X"])  # should create JSON file
    assert res.exit_code == 0
    # Validate we wrote JSON (not SQLite header)
    loaded = json.loads(data_path.read_text())
    assert isinstance(loaded, list)


def test_ext_db_forces_sqlite_backend(tmp_path: Path, monkeypatch) -> None:
    """.db path uses SQLite backend even if config says json."""
    cli = _reload_cli(tmp_path, monkeypatch)
    import loopbloom.core.config as cfg

    cfg.save({"storage": "json"})
    data_path = tmp_path / "data.db"
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(data_path))

    runner = CliRunner()
    res = runner.invoke(cli, ["goal", "add", "Y"])  # should create SQLite DB
    assert res.exit_code == 0
    # Validate SQLite file signature
    sig = data_path.read_bytes()[:15]
    assert sig == b"SQLite format 3"
