"""Additional tests to reach 100% coverage."""

from __future__ import annotations

import importlib
from pathlib import Path

import click
import pytest
from click.testing import CliRunner


class DummyStore:
    """Minimal Storage implementation for testing ``Storage.lock``."""

    def load(self):
        """Return an empty list of goals."""
        return []

    def save(self, goals):
        """Pretend to persist ``goals``."""
        pass


def test_storage_base_lock_context_manager():
    """Ensure ``Storage.lock`` acts as a context manager."""
    from loopbloom.storage.base import Storage

    class DS(DummyStore, Storage):
        pass

    ds = DS()
    with ds.lock():
        assert True


def test_json_store_lock(tmp_path: Path) -> None:
    """Check that ``JSONStore.lock`` acquires and releases properly."""
    from loopbloom.storage.json_store import JSONStore

    store = JSONStore(path=tmp_path / "d.json")
    with store.lock():
        assert store.load() == []


def test_talkpool_random_fallback() -> None:
    """Fallback to default pep talk if the key is unknown."""
    from loopbloom.core.talks import TalkPool

    original = TalkPool._cache
    TalkPool._cache = {"success": ["great"]}
    try:
        assert TalkPool.random("bogus") == "Great job!"
    finally:
        TalkPool._cache = original


def test_notifier_none_mode(capsys):
    """Ensure notifier does nothing when mode is ``none``."""
    from loopbloom.services import notifier

    notifier.send("Title", "Msg", mode="none")
    assert capsys.readouterr().out == ""


def test_notifier_exception_fallback(monkeypatch, capsys):
    """Fallback to terminal if plyer raises an exception."""
    from loopbloom.services import notifier

    class Bad:
        def notify(self, *_, **__):
            raise RuntimeError("boom")

    monkeypatch.setattr(notifier, "notification", Bad())
    notifier.send("T", "M", mode="desktop")
    out = capsys.readouterr().out
    assert "falling back to terminal" in out


def test_step_validation_error():
    """Step creation with invalid data should raise an error."""
    from loopbloom.core.coping import CopingPlanError, Step

    with pytest.raises(CopingPlanError):
        Step({})


# --- CLI edge cases ------------------------------------------------------


def _reload_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Reload CLI modules with data path at ``tmp_path``."""
    import loopbloom.cli as cli_mod
    import loopbloom.storage.json_store as js_mod
    from loopbloom import __main__ as main

    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))
    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(main)
    return main.cli


def test_goal_list_empty(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """List goals when the store is empty."""
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    # ensure file exists but empty
    JSONStore(path=tmp_path / "data.json").save([])
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(cli, ["goal", "list"], env=env)
    assert "No goals" in res.output


def test_goal_rm_requires_confirm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Deletion without ``--yes`` requires confirmation."""
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    store = JSONStore(path=tmp_path / "data.json")
    store.save([GoalArea(name="X")])
    monkeypatch.setattr(click, "confirm", lambda *a, **k: False)
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(cli, ["goal", "rm", "X"], env=env)
    assert "Deleted" not in res.output


def test_goal_rm_yes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Delete a goal immediately with ``--yes``."""
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    store = JSONStore(path=tmp_path / "data.json")
    store.save([GoalArea(name="X")])
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(cli, ["goal", "rm", "X", "--yes"], env=env)
    assert "Deleted goal" in res.output


def test_phase_rm_requires_confirm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Deleting a phase without ``--yes`` asks for confirmation."""
    from loopbloom.core.models import GoalArea, Phase
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    store = JSONStore(path=tmp_path / "data.json")
    store.save([GoalArea(name="G", phases=[Phase(name="P")])])
    monkeypatch.setattr(click, "confirm", lambda *a, **k: False)
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(cli, ["goal", "phase", "rm", "G", "P"], env=env)
    assert "Deleted" not in res.output


def test_phase_rm_yes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove a phase immediately with ``--yes``."""
    from loopbloom.core.models import GoalArea, Phase
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    store = JSONStore(path=tmp_path / "data.json")
    store.save([GoalArea(name="G", phases=[Phase(name="P")])])
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(
        cli,
        ["goal", "phase", "rm", "G", "P", "--yes"],
        env=env,
    )
    assert "Deleted phase" in res.output


def test_micro_add_missing_phase(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Adding a micro-habit requires the phase to exist."""
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    JSONStore(path=tmp_path / "data.json").save([GoalArea(name="G")])
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(
        cli,
        ["goal", "micro", "add", "M", "--goal", "G", "--phase", "P"],
        env=env,
    )
    assert "Created phase 'P'" in res.output
    assert "Added micro-habit" in res.output


def test_micro_cancel_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Canceling a missing micro-habit should print an error."""
    from loopbloom.core.models import GoalArea, Phase
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    g = GoalArea(name="G", phases=[Phase(name="P", micro_goals=[])])
    JSONStore(path=tmp_path / "data.json").save([g])
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(
        cli,
        ["goal", "micro", "rm", "M", "--goal", "G", "--phase", "P"],
        env=env,
    )
    assert "Micro-habit 'M' not found" in res.output


def test_micro_cancel_no_phase(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Canceling with a missing phase should notify the user."""
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    JSONStore(path=tmp_path / "data.json").save([GoalArea(name="G")])
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(
        cli,
        ["goal", "micro", "rm", "M", "--goal", "G", "--phase", "P"],
        env=env,
    )
    assert "Phase 'P' not found" in res.output


def test_checkin_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Handle check-ins when goals or micro-habits are absent."""
    from loopbloom.core.models import GoalArea, MicroGoal, Phase
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(cli, ["checkin", "G"], env=env)
    assert "Goal not found" in res.output
    g = GoalArea(
        name="G",
        phases=[
            Phase(
                name="P",
                micro_goals=[MicroGoal(name="M", status="complete")],
            )
        ],
    )
    JSONStore(path=tmp_path / "data.json").save([g])
    res = runner.invoke(cli, ["checkin", "G"], env=env)
    assert "No active micro" in res.output


def test_summary_edge_cases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Summary command handles missing goal or active micro."""
    from loopbloom.core.models import GoalArea, Phase
    from loopbloom.storage.json_store import JSONStore

    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    res = runner.invoke(cli, ["summary", "--goal", "G"], env=env)
    assert "Goal not found" in res.output
    JSONStore(path=tmp_path / "data.json").save(
        [GoalArea(name="G", phases=[Phase(name="P")])]
    )
    res = runner.invoke(cli, ["summary", "--goal", "G"], env=env)
    assert "No active micro" in res.output
    res = runner.invoke(cli, ["summary"], env=env)
    assert "LoopBloom Progress" in res.output


def test_config_branches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercise ``config`` CLI paths and config module reloads."""
    import loopbloom.cli.config as config_mod
    import loopbloom.core.config as cfg_mod
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
