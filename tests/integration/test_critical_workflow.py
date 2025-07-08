"""
Integration test for the critical user workflow.
1. Add a goal.
2. Add a micro-habit to that goal.
"""

from click.testing import CliRunner
from loopbloom.__main__ import cli


def test_critical_workflow_failure(tmp_path) -> None:
    """Tests adding a goal then a micro-habit."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # 1. Add a goal
    result_add_goal = runner.invoke(
        cli,
        ["goal", "add", "Test Goal"],
        env=env,
    )
    assert result_add_goal.exit_code == 0
    assert "Added goal" in result_add_goal.output

    # 2. Add a micro-habit to the goal
    result_add_micro = runner.invoke(
        cli,
        ["micro", "add", "Test Micro", "--goal", "Test Goal"],
        env=env,
    )

    # 3. Assert that the command succeeds
    assert result_add_micro.exit_code == 0
    assert "Added micro-habit" in result_add_micro.output
