"""Integration tests for the tree CLI command."""

import os

from click.testing import CliRunner


def test_tree_displays_hierarchy(tmp_path) -> None:
    """Ensure tree output includes goal, phase, and micro names."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    from loopbloom import __main__ as main

    cli = main.cli

    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "phase", "add", "Exercise", "Base"], env=env)
    runner.invoke(
        cli,
        [
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
