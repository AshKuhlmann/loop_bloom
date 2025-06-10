"""Integration tests for check-in and summary commands."""

from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_checkin_generates_peptalk_and_summary(tmp_path) -> None:
    """Check that `checkin` stores data and `summary` displays it."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Setup – create goal/phase/micro via Phase 2 commands
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "phase", "add", "Exercise", "Foundation"], env=env)
    runner.invoke(
        cli,
        ["goal", "micro", "add", "Exercise", "Foundation", "Walk 5 min"],
        env=env,
    )

    # Run check-in (success)
    res = runner.invoke(cli, ["checkin", "Exercise", "--success"], env=env)
    assert "✓" in res.output or "Amazing" in res.output

    # Summary per-goal
    res = runner.invoke(cli, ["summary", "--goal", "Exercise"], env=env)
    assert "Exercise" in res.output and "Walk 5 min" in res.output
