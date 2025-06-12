"""Integration tests for the goal CLI."""

import json
import os

from click.testing import CliRunner


def test_goal_phase_micro_crud(tmp_path):
    """End-to-end CRUD interactions via the CLI."""
    runner = CliRunner()
    # Use an isolated JSON path
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    if data_file.exists():
        data_file.unlink()

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    import importlib

    import loopbloom.cli as cli_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.storage.json_store as js_mod
    from loopbloom import __main__ as main

    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(goal_mod)
    importlib.reload(main)
    cli = main.cli

    # Add a goal
    res = runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    assert res.exit_code == 0 and "Added goal:" in res.output

    # List goals
    res = runner.invoke(cli, ["goal", "list"], env=env)
    assert "Exercise" in res.output

    # Add phase
    res = runner.invoke(
        cli,
        ["goal", "phase", "add", "Exercise", "Foundation"],
        env=env,
    )
    assert res.exit_code == 0

    # Add micro-habit
    res = runner.invoke(
        cli,
        [
            "goal",
            "micro",
            "add",
            "Walk 5 min",
            "--goal",
            "Exercise",
            "--phase",
            "Foundation",
        ],
        env=env,
    )
    assert "Added micro-habit" in res.output

    # Cancel micro-habit
    res = runner.invoke(
        cli,
        [
            "goal",
            "micro",
            "rm",
            "Walk 5 min",
            "--goal",
            "Exercise",
            "--phase",
            "Foundation",
            "--yes",
        ],
        env=env,
    )
    assert "Deleted micro-habit" in res.output

    # Verify JSON structure saved
    data = json.loads(data_file.read_text())
    assert data[0]["phases"][0]["micro_goals"] == []


def test_goal_rm_missing(tmp_path) -> None:
    """Attempting to remove an unknown goal shows an error."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    import importlib

    import loopbloom.cli as cli_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.storage.json_store as js_mod
    from loopbloom import __main__ as main

    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(goal_mod)
    importlib.reload(main)
    cli = main.cli

    res = runner.invoke(cli, ["goal", "rm", "Ghost", "--yes"], env=env)
    assert "Goal not found" in res.output


def test_phase_add_missing_goal(tmp_path) -> None:
    """Adding a phase to a nonexistent goal yields an error message."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    import importlib

    import loopbloom.cli as cli_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.storage.json_store as js_mod
    from loopbloom import __main__ as main

    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(goal_mod)
    importlib.reload(main)
    cli = main.cli

    res = runner.invoke(
        cli,
        ["goal", "phase", "add", "Ghost", "Base"],
        env=env,
    )
    assert "[red]Goal not found" in res.output
