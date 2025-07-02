"""Integration tests for check-in and summary commands."""

from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_checkin_generates_peptalk_and_summary(tmp_path) -> None:
    """Check that `checkin` stores data and `summary` displays it."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Setup – create goal/phase/micro via Phase 2 commands
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(
        cli,
        ["goal", "phase", "add", "Exercise", "Foundation"],
        env=env,
    )
    runner.invoke(
        cli,
        [
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

    # Run check-in (success)
    res = runner.invoke(cli, ["checkin", "Exercise", "--success"], env=env)
    assert any(k in res.output for k in ("✓", "Amazing", "Awesome"))

    # Summary per-goal
    res = runner.invoke(cli, ["summary", "--goal", "Exercise"], env=env)
    assert "Exercise" in res.output and "Walk 5 min" in res.output


def test_goal_specific_progress(tmp_path) -> None:
    """Detailed success stats show for a single goal."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Create goal and micro-habit
    runner.invoke(cli, ["goal", "add", "Focus"], env=env)
    runner.invoke(cli, ["micro", "add", "Meditate", "--goal", "Focus"], env=env)

    # Log multiple check-ins
    for _ in range(3):
        runner.invoke(cli, ["checkin", "Focus", "--success"], env=env)

    res = runner.invoke(cli, ["summary", "--goal", "Focus"], env=env)
    assert "Focus" in res.output and "Meditate" in res.output
    assert "Success rate last" in res.output
