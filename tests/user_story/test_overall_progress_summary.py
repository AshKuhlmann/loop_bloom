"""End-to-end test covering overall progress summary across multiple goals."""

from datetime import date, timedelta

from click.testing import CliRunner

from loopbloom import __main__ as main
from loopbloom.core.models import Checkin
from loopbloom.storage.json_store import JSONStore


def test_overall_progress_summary(tmp_path) -> None:
    """Summary shows streak banner for each goal."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    cli = main.cli

    goals = ["G1", "G2", "G3"]
    for g in goals:
        assert runner.invoke(cli, ["goal", "add", g], env=env).exit_code == 0
        result = runner.invoke(
            cli,
            ["micro", "add", "Task", "--goal", g],
            env=env,
        )
        assert result.exit_code == 0

    store = JSONStore(path=data_file)
    data = store.load()
    patterns = [
        [True] * 14,  # always success -> should advance
        [True, False] * 7,  # 50 % success -> no advance
        [True] * 12 + [False] * 2,  # ~85 % success -> should advance
    ]
    for goal_obj, pat in zip(data, patterns):
        goal_obj.micro_goals[0].checkins = [
            Checkin(
                date=date.today() - timedelta(days=i),
                success=s,
            )
            for i, s in enumerate(pat)
        ]
    store.save(data)

    res = runner.invoke(cli, ["summary"], env=env)
    out = res.output
    assert "LoopBloom Progress" in out
    for name in goals:
        assert name in out
    assert out.count("Advance?") == 2
