import os
from click.testing import CliRunner


def test_add_new_goal(tmp_path) -> None:
    """Add goal then verify it shows up in goal list."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    from loopbloom import __main__ as main
    cli = main.cli

    res = runner.invoke(cli, ["goal", "add", "New Goal"], env=env)
    assert res.exit_code == 0
    assert "Added goal:" in res.output

    res = runner.invoke(cli, ["goal", "list"], env=env)
    assert "New Goal" in res.output
