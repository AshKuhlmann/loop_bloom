"""Additional tests to reach 100% coverage."""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import click
from click.testing import CliRunner
import pytest


class DummyStore:
    """Minimal Storage implementation for testing base.lock."""

    def load(self):
        return []

    def save(self, goals):
        pass



def test_storage_base_lock_context_manager():
    from loopbloom.storage.base import Storage

    class DS(DummyStore, Storage):
        pass

    ds = DS()
    with ds.lock():
        assert True


def test_json_store_lock(tmp_path: Path) -> None:
    from loopbloom.storage.json_store import JSONStore

    store = JSONStore(path=tmp_path / "d.json")
    with store.lock():
        assert store.load() == []


def test_talkpool_random_fallback() -> None:
    from loopbloom.core.talks import TalkPool

    original = TalkPool._cache
    TalkPool._cache = {"success": ["great"]}
    try:
        assert TalkPool.random("bogus") == "Great job!"
    finally:
        TalkPool._cache = original


def test_notifier_none_mode(capsys):
    from loopbloom.services import notifier

    notifier.send("Title", "Msg", mode="none")
    assert capsys.readouterr().out == ""


def test_step_validation_error():
    from loopbloom.core.coping import Step, CopingPlanError

    with pytest.raises(CopingPlanError):
        Step({})


# --- CLI edge cases ------------------------------------------------------

def _reload_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    import os
    from loopbloom import __main__ as main
    import loopbloom.cli as cli_mod
    import loopbloom.storage.json_store as js_mod

    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))
    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(main)
    return main.cli


def test_goal_list_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    # ensure file exists but empty
    JSONStore(path=tmp_path / "data.json").save([])
    res = runner.invoke(cli, ["goal", "list"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "No goals" in res.output


def test_goal_rm_requires_confirm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    store = JSONStore(path=tmp_path/"data.json")
    store.save([GoalArea(name="X")])
    monkeypatch.setattr(click, "confirm", lambda *a, **k: False)
    runner = CliRunner()
    res = runner.invoke(cli, ["goal", "rm", "X"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "Deleted" not in res.output


def test_goal_rm_yes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    store = JSONStore(path=tmp_path/"data.json")
    store.save([GoalArea(name="X")])
    runner = CliRunner()
    res = runner.invoke(cli, ["goal", "rm", "X", "--yes"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "Deleted goal" in res.output


def test_micro_add_missing_phase(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    JSONStore(path=tmp_path/"data.json").save([GoalArea(name="G")])
    runner = CliRunner()
    res = runner.invoke(cli, ["goal", "micro", "add", "G", "P", "M"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "Goal or phase not found" in res.output


def test_micro_cancel_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea, Phase
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    g = GoalArea(name="G", phases=[Phase(name="P", micro_goals=[])])
    JSONStore(path=tmp_path/"data.json").save([g])
    runner = CliRunner()
    res = runner.invoke(cli, ["goal", "micro", "cancel", "G", "P", "M"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "Micro-habit not found" in res.output


def test_micro_cancel_no_phase(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    JSONStore(path=tmp_path/"data.json").save([GoalArea(name="G")])
    runner = CliRunner()
    res = runner.invoke(cli, ["goal", "micro", "cancel", "G", "P", "M"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "Goal or phase not found" in res.output


def test_checkin_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea, Phase, MicroGoal
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    res = runner.invoke(cli, ["checkin", "G"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "Goal not found" in res.output
    g = GoalArea(name="G", phases=[Phase(name="P", micro_goals=[MicroGoal(name="M", status="complete")])])
    JSONStore(path=tmp_path/"data.json").save([g])
    res = runner.invoke(cli, ["checkin", "G"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "No active micro" in res.output


def test_summary_edge_cases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom.core.models import GoalArea, Phase
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    res = runner.invoke(cli, ["summary", "--goal", "G"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "Goal not found" in res.output
    JSONStore(path=tmp_path/"data.json").save([GoalArea(name="G", phases=[Phase(name="P")])])
    res = runner.invoke(cli, ["summary", "--goal", "G"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "No active micro" in res.output
    res = runner.invoke(cli, ["summary"], env={"LOOPBLOOM_DATA_PATH": str(tmp_path/"data.json")})
    assert "LoopBloom Progress" in res.output


def test_config_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import os
    import loopbloom.core.config as cfg_mod
    import loopbloom.cli.config as config_mod
    from loopbloom import __main__ as main

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    importlib.reload(cfg_mod)
    importlib.reload(config_mod)
    importlib.reload(main)
    cli = main.cli

    runner = CliRunner()
    runner.invoke(cli, ["config", "set", "advance.window", "7"])
    runner.invoke(cli, ["config", "set", "notify", "true"])
    res = runner.invoke(cli, ["config", "get", "missing.key"])
    assert "Key not found" in res.output
    cfg = cfg_mod.load()
    assert cfg["advance"]["window"] == 7
    assert cfg["notify"] is True
    # restore default config module state
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    importlib.reload(cfg_mod)
