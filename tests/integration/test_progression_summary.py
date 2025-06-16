"""Integration test covering automatic advancement prompt."""

from datetime import date, timedelta

from click.testing import CliRunner

from loopbloom.core.models import Checkin


def _generate_success_history(ratio_target=0.85):
    checks = []
    successes = int(round(14 * ratio_target))
    for i in range(14):
        check_date = date.today() - timedelta(days=i)
        checks.append(Checkin(date=check_date, success=i < successes))
    return checks


def test_summary_shows_advance_prompt(tmp_path):
    """Ensure summary highlights advancement when criteria met."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    import os

    os.environ["LOOPBLOOM_DATA_PATH"] = env["LOOPBLOOM_DATA_PATH"]

    from loopbloom import __main__ as main

    cli = main.cli

    # Setup
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

    # Inject fake history (>80 %)
    from loopbloom.storage.json_store import JSONStore

    store = JSONStore(path=env["LOOPBLOOM_DATA_PATH"])
    goals = store.load()
    goals[0].phases[0].micro_goals[0].checkins = _generate_success_history()
    store.save(goals)

    res = runner.invoke(cli, ["summary", "--goal", "Exercise"], env=env)
    assert "Advance?" in res.output
