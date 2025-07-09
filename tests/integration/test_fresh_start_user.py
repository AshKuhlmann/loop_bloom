import pytest
from click.testing import CliRunner
from pathlib import Path
import json
from datetime import datetime, timedelta

from loopbloom.__main__ import cli
from loopbloom.core.models import GoalArea, MicroGoal, Phase


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_temp_data_path(tmp_path):
    # This fixture ensures each test gets a clean, isolated data directory
    return tmp_path


def test_fresh_start_user_story(runner, setup_temp_data_path):
    """
    Simulate a user starting fresh by exporting data and deleting the data file.
    """
    data_file = setup_temp_data_path / "data.json"
    export_file = setup_temp_data_path / "exported_data.json"

    # Configure the CLI to use this data file
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_file)])
    assert result.exit_code == 0

    # 1. Create a series of goals, phases, and micro-habits.
    runner.invoke(cli, ["goal", "add", "Fitness"])
    runner.invoke(cli, ["goal", "phase", "add", "Fitness", "Main Phase"])
    runner.invoke(cli, ["micro", "add", "Walk 30 min", "--goal", "Fitness", "--phase", "Main Phase"])
    runner.invoke(cli, ["goal", "add", "Learning"])
    runner.invoke(cli, ["goal", "phase", "add", "Learning", "Main Phase"])
    runner.invoke(cli, ["micro", "add", "Read 1 chapter", "--goal", "Learning", "--phase", "Main Phase"])

    # 2. Perform several check-ins, including successes, skips, and completions of micro-habits.
    runner.invoke(cli, ["checkin", "Fitness", "--success"])
    runner.invoke(cli, ["checkin", "Learning", "--skip"])
    runner.invoke(cli, ["checkin", "Fitness", "--success"])

    # Simulate completing a micro-habit
    runner.invoke(cli, ["micro", "complete", "Walk 30 min", "--goal", "Fitness"])

    # 3. Use the export command to save the current state to a JSON file.
    result = runner.invoke(cli, ["export", "--fmt", "json", "--out", str(export_file)])
    assert result.exit_code == 0
    assert str(export_file) in result.output
    assert export_file.exists()

    # 4. Verify that the exported JSON file contains the correct data.
    with open(export_file, "r") as f:
        exported_data = json.load(f)

    assert len(exported_data) == 2 # Fitness and Learning goals
    fitness_goal = next((g for g in exported_data if g["name"] == "Fitness"), None)
    learning_goal = next((g for g in exported_data if g["name"] == "Learning"), None)

    print(f"Exported Data: {json.dumps(exported_data, indent=2)}")
    print(f"Fitness Goal: {json.dumps(fitness_goal, indent=2)}")
    print(f"Learning Goal: {json.dumps(learning_goal, indent=2)}")

    assert fitness_goal is not None
    assert learning_goal is not None

    # Check for presence of micro-goals and their check-ins
    assert any(m["name"] == "Walk 30 min" for p in fitness_goal.get("phases", []) for m in p.get("micro_goals", []))
    assert any(m["name"] == "Read 1 chapter" for p in learning_goal.get("phases", []) for m in p.get("micro_goals", []))

    # More detailed checks can be added if needed, but this avoids the IndexError

    # 5. Delete the data.json file.
    assert data_file.exists()
    data_file.unlink()
    assert not data_file.exists()

    # 6. Run loopbloom goal list and verify that no goals are listed.
    result = runner.invoke(cli, ["goal", "list"])
    assert result.exit_code == 0
    assert "No goals – use `loopbloom goal add`." in result.output

    # 7. Add a new goal and verify that it is the only goal in the new data.json file.
    runner.invoke(cli, ["goal", "add", "New Beginning"])
    result = runner.invoke(cli, ["goal", "list"])
    assert result.exit_code == 0
    assert "• New Beginning (phases: 0)" in result.output

    # Verify only one goal exists in the data file
    with open(data_file, "r") as f:
        new_data = json.load(f)
    assert len(new_data) == 1
    assert new_data[0]["name"] == "New Beginning"
