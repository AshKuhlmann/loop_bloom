"""Integration tests for direct micro-goal workflows."""

import importlib
import json
import os

from click.testing import CliRunner


def _reload_cli_modules():
    """Reload CLI modules to pick up changes."""
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import loopbloom.cli as cli_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.cli.tree as tree_mod
    import loopbloom.storage.json_store as js_mod
    from loopbloom import __main__ as main

    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(goal_mod)
    importlib.reload(tree_mod)
    importlib.reload(main)
    return main.cli


def test_direct_microgoal_workflow(tmp_path):
    """Test CRUD, tree, and check-in for phase-less micro-goals."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    # Ensure env var is set for reloads
    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    cli = _reload_cli_modules()

    # 1. Add Goal
    runner.invoke(cli, ["goal", "add", "Reading"], env=env)

    # 2. Add Micro-Goal directly to Goal
    res_add = runner.invoke(
        cli,
        ["goal", "micro", "add", "Read 1 page", "--goal", "Reading"],
        env=env,
    )
    assert res_add.exit_code == 0
    assert "Added micro-habit 'Read 1 page' to goal 'Reading'" in res_add.output

    # 3. Verify with `tree`
    res_tree = runner.invoke(cli, ["tree"], env=env)
    assert "Reading" in res_tree.output
    assert "Phase" not in res_tree.output
    assert "Read 1 page" in res_tree.output

    # 4. Edit micro-goal
    res_edit = runner.invoke(
        cli,
        [
            "goal",
            "micro",
            "edit",
            "Read 1 page",
            "--new-name",
            "Read 2 pages",
            "--goal",
            "Reading",
        ],
        env=env,
    )
    assert "Updated micro-habit" in res_edit.output

    # 5. Check in
    res_checkin = runner.invoke(cli, ["checkin", "Reading"], env=env)
    assert "\u2713" in res_checkin.output

    data = json.loads(data_file.read_text())
    assert len(data[0]["micro_goals"][0]["checkins"]) == 1

    # 6. Remove micro-goal
    res_rm = runner.invoke(
        cli,
        ["goal", "micro", "rm", "Read 2 pages", "--goal", "Reading", "--yes"],
        env=env,
    )
    assert "Deleted micro-habit" in res_rm.output

    data_after_rm = json.loads(data_file.read_text())
    assert len(data_after_rm[0]["micro_goals"]) == 0
