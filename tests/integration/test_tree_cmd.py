"""Integration tests for the tree CLI command."""

import importlib
import os

from click.testing import CliRunner


def test_tree_displays_hierarchy(tmp_path) -> None:
    """Ensure tree output includes goal, phase, and micro names."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

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

    cli = main.cli

    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "phase", "add", "Exercise", "Base"], env=env)
    runner.invoke(
        cli,
        [
            "goal",
            "micro",
            "add",
            "Walk",
            "--goal",
            "Exercise",
            "--phase",
            "Base",
        ],
        env=env,
    )

    res = runner.invoke(cli, ["tree"], env=env)
    assert "Exercise" in res.output
    assert "Base" in res.output
    assert "Walk" in res.output
