"""End-to-end scenario covering multi-goal progression."""

import os
import random
import string
from datetime import date, timedelta

from click.testing import CliRunner

from loopbloom import __main__ as main
from loopbloom.core.models import Checkin, Status
from loopbloom.storage.json_store import JSONStore


def _randstr(n: int) -> str:
    """Return a random alphabetic string of length ``n``."""
    return "".join(random.choice(string.ascii_letters) for _ in range(n))


def test_multi_goal_progression(tmp_path):
    """Goals progress to the next micro-habit after sustained success."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}
    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    cli = main.cli

    random.seed(42)
    goals = [_randstr(8) for _ in range(3)]
    subgoals = [[_randstr(6) for _ in range(3)] for _ in range(3)]

    # create goals and subgoals
    for idx, g in enumerate(goals):
        res = runner.invoke(cli, ["goal", "add", g], env=env)
        assert res.exit_code == 0
        for sg in subgoals[idx]:
            r = runner.invoke(cli, ["micro", "add", sg, "--goal", g], env=env)
            assert r.exit_code == 0

    # inject 14 successful checkins for first subgoal of each goal
    store = JSONStore(path=data_file)
    data = store.load()
    for g in data:
        mg = g.micro_goals[0]
        mg.checkins = [
            Checkin(date=date.today() - timedelta(days=i), success=True)
            for i in range(14)
        ]
    store.save(data)

    # summary should suggest advancement
    for g in goals:
        res = runner.invoke(cli, ["summary", "--goal", g], env=env)
        assert "Advance?" in res.output

    # complete first subgoal and verify the next becomes active
    for idx, g in enumerate(goals):
        first = subgoals[idx][0]
        res = runner.invoke(
            cli,
            ["micro", "complete", first, "--goal", g],
            env=env,
        )
        assert res.exit_code == 0
        assert "Marked micro-habit" in res.output

    updated = store.load()
    for idx, g in enumerate(updated):
        assert g.micro_goals[0].status == Status.complete
        assert g.get_active_micro_goal().name == subgoals[idx][1]
