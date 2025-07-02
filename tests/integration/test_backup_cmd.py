"""Integration test for the ``backup`` command."""

import importlib
from pathlib import Path

from click.testing import CliRunner


def test_backup_creates_file(tmp_path, monkeypatch):
    """Running ``backup`` copies the active data file."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    data_file = tmp_path / "data.json"
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(data_file))
    monkeypatch.delenv("LOOPBLOOM_SQLITE_PATH", raising=False)

    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    import loopbloom.__main__ as main

    importlib.reload(main)

    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    runner.invoke(main.cli, ["goal", "add", "Keep"], env=env)
    res = runner.invoke(main.cli, ["backup"], env=env)
    assert res.exit_code == 0
    backup_dir = Path(tmp_path) / "loopbloom" / "backups"
    files = list(backup_dir.iterdir())
    assert files and "backup" in files[0].name
