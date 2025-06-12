"""Tests for interactive selection menus."""

import importlib
import json
import os

from click.testing import CliRunner

from loopbloom import __main__ as main


def test_checkin_prompts_for_goal(tmp_path) -> None:
    """Check that missing args trigger goal selection prompt."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(tmp_path / "data.json")
    import loopbloom.cli as cli_mod
    import loopbloom.cli.checkin as checkin_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.storage.json_store as js_mod

    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(goal_mod)
    importlib.reload(checkin_mod)
    importlib.reload(main)
    cli = main.cli

    # setup
    runner.invoke(cli, ["goal", "add", "Sleep"], env=env)
    runner.invoke(cli, ["goal", "phase", "add", "Sleep", "Base"], env=env)
    runner.invoke(
        cli,
        ["goal", "micro", "add", "Sleep", "Base", "Lights"],
        env=env,
    )

    res = runner.invoke(cli, ["checkin"], env=env, input="1\n")
    assert "Which goal do you want to check in for?" in res.output

    data = json.loads((tmp_path / "data.json").read_text())
    checks = data[0]["phases"][0]["micro_goals"][0]["checkins"]
    assert len(checks) == 1
