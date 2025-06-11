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
    monkeypatch.setenv("LOOPBLOOM_SQLITE_PATH", str(db_path))
    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    runner.invoke(cli, ["config", "set", "storage", "sqlite"])
    import loopbloom.__main__ as main
    import loopbloom.cli as cli_mod
    import loopbloom.storage.sqlite_store as sql_mod

    importlib.reload(cfg_mod)
    importlib.reload(sql_mod)
    importlib.reload(cli_mod)
    importlib.reload(main)
    new_cli = main.cli

    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "dummy.json")}
    runner.invoke(new_cli, ["goal", "add", "NotifyGoal"], env=env)
    runner.invoke(new_cli, ["goal", "phase", "add", "NotifyGoal", "Base"], env=env)
    runner.invoke(
        new_cli,
        ["goal", "micro", "add", "NotifyGoal", "Base", "Test"],
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
    runner.invoke(new_cli, ["config", "set", "notify", "desktop"])
    runner.invoke(new_cli, ["checkin", "NotifyGoal"], env=env)
    assert "\u2713" in calls.get("msg", "") or "Great" in calls.get("msg", "")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    importlib.reload(cfg_mod)
