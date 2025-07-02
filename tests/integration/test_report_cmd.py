"""Integration test for the report command."""

from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_report_command_outputs(tmp_path) -> None:  # noqa: D103
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Setup basic goal and micro-goal
    runner.invoke(cli, ["goal", "add", "Health"], env=env)
    runner.invoke(cli, ["micro", "add", "Walk", "--goal", "Health"], env=env)
    runner.invoke(cli, ["checkin", "Health"], env=env)

    res = runner.invoke(cli, ["report", "--mode", "success"], env=env)
    assert "Health" in res.output
    res2 = runner.invoke(cli, ["report", "--mode", "calendar"], env=env)
    assert "Heatmap" in res2.output
    res3 = runner.invoke(cli, ["report", "--mode", "line"], env=env)
    assert "Success Rate" in res3.output
