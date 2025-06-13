"""Unit tests for micro CLI commands."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from click.testing import CliRunner


def _reload_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Reload CLI modules with custom data path."""
    import loopbloom.cli as cli_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.cli.micro as micro_mod
    import loopbloom.storage.json_store as js_mod
    from loopbloom import __main__ as main

    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))
    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(goal_mod)
    importlib.reload(micro_mod)
    importlib.reload(main)
    return main.cli


def test_micro_complete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Marking a micro-habit complete updates its status."""
    from loopbloom.core.models import GoalArea, MicroGoal
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    store = JSONStore(path=tmp_path / "data.json")
    store.save([GoalArea(name="G", micro_goals=[MicroGoal(name="M")])])

    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(
        cli,
        ["micro", "complete", "M", "--goal", "G"],
        env=env,
    )
    assert "complete" in res.output
    data = store.load()
    assert data[0].micro_goals[0].status == "complete"


def test_micro_cancel_phase_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing phase triggers an error message."""
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    JSONStore(path=tmp_path / "data.json").save([GoalArea(name="G")])
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(
        cli,
        [
            "micro",
            "cancel",
            "M",
            "--goal",
            "G",
            "--phase",
            "P",
        ],
        env=env,
    )
    assert "Phase 'P' not found" in res.output


def test_micro_complete_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Completing a nonexistent micro-habit warns the user."""
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    JSONStore(path=tmp_path / "data.json").save([GoalArea(name="G")])
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(
        cli,
        ["micro", "complete", "M", "--goal", "G"],
        env=env,
    )
    assert "Micro-habit 'M' not found" in res.output
