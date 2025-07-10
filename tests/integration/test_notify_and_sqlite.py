"""Integration tests for desktop notifications and SQLite storage."""

import importlib
from pathlib import Path

from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_switch_to_sqlite_and_notify(tmp_path, monkeypatch):
    """Switch backend and ensure notify call occurs."""
    runner = CliRunner()
    db_path = tmp_path / "db.sqlite"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    # Use the correct environment variables
    monkeypatch.setenv("LOOPBLOOM_STORAGE_BACKEND", "sqlite")
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(db_path))

    import loopbloom.core.config as cfg_mod
    import loopbloom.__main__ as main

    # Reload the modules to pick up the new environment variables
    importlib.reload(cfg_mod)
    importlib.reload(main)

    # No need to set the storage backend via the CLI, it's already set by the environment variable

    env = {"LOOPBLOOM_DATA_PATH": str(db_path)}
    runner.invoke(main.cli, ["goal", "add", "NotifyGoal"], env=env)
    runner.invoke(
        main.cli,
        ["goal", "phase", "add", "NotifyGoal", "Base"],
        env=env,
    )
    runner.invoke(
        main.cli,
        [
            "micro",
            "add",
            "Test",
            "--goal",
            "NotifyGoal",
            "--phase",
            "Base",
        ],
        env=env,
    )

    assert db_path.exists(), "SQLite DB created"

    calls = {}

    def fake_notify(title, message, timeout):
        calls["msg"] = message

    monkeypatch.setattr(
        "loopbloom.services.notifier.notification",
        type("X", (), {"notify": fake_notify}),
    )
    runner.invoke(main.cli, ["config", "set", "notify", "desktop"])
    runner.invoke(main.cli, ["checkin", "NotifyGoal"], env=env)
    assert "\u2713" in calls.get("msg", "") or "Great" in calls.get("msg", "")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    importlib.reload(cfg_mod)
