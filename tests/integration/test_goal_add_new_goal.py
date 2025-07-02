"""Integration tests covering goal creation and listing."""

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


def test_goal_list_multiple_goals(tmp_path) -> None:
    """View all goals after adding several."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    from loopbloom import __main__ as main

    cli = main.cli

    for name in ["Goal A", "Goal B", "Goal C"]:
        res = runner.invoke(cli, ["goal", "add", name], env=env)
        assert res.exit_code == 0

    res = runner.invoke(cli, ["goal", "list"], env=env)
    for name in ["Goal A", "Goal B", "Goal C"]:
        assert name in res.output


def test_remove_goal(tmp_path) -> None:
    """Add then remove a goal via the CLI."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    from loopbloom import __main__ as main

    cli = main.cli

    # Add the goal
    res = runner.invoke(cli, ["goal", "add", "Goal to Remove"], env=env)
    assert res.exit_code == 0

    # Remove the goal
    res = runner.invoke(
        cli,
        ["goal", "rm", "Goal to Remove", "--yes"],
        env=env,
    )
    assert res.exit_code == 0
    assert "Deleted goal" in res.output

    # Verify it no longer appears in list
    res = runner.invoke(cli, ["goal", "list"], env=env)
    assert "Goal to Remove" not in res.output
