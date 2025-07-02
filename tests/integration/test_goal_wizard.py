import json
import os

from click.testing import CliRunner


def test_goal_wizard_creates_hierarchy(tmp_path) -> None:
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    from loopbloom import __main__ as main

    cli = main.cli

    user_input = "\n".join(["Fitness", "Base", "Stretch"])
    res = runner.invoke(cli, ["goal", "wizard"], env=env, input=user_input)
    assert res.exit_code == 0
    assert "Created goal" in res.output

    data = json.loads(data_file.read_text())
    assert data[0]["name"] == "Fitness"
    assert data[0]["phases"][0]["name"] == "Base"
    assert data[0]["phases"][0]["micro_goals"][0]["name"] == "Stretch"
