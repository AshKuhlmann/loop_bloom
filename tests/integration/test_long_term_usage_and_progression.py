import os
import json
import pytest
from click.testing import CliRunner
from datetime import datetime, timedelta

from loopbloom.__main__ import cli
from loopbloom.core.models import Checkin, GoalArea, MicroGoal, Phase


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_temp_data_path(tmp_path, monkeypatch):
    # This fixture ensures each test gets a clean, isolated data directory
    # and sets the LOOPBLOOM_DATA_PATH environment variable.
    data_file = tmp_path / "data.json"
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(data_file))
    # Set a fixed debug date for consistent test results
    monkeypatch.setenv("LOOPBLOOM_DEBUG_DATE", "2025-07-09")
    return tmp_path


def test_progression_engine_suggests_advancement(runner, setup_temp_data_path):
    """
    Test that the progression engine correctly suggests advancement
    after sufficient successful check-ins.
    """
    data_path = setup_temp_data_path / "data.json"

    # Use the fixed debug date for generating check-ins
    fixed_today = datetime.strptime(os.environ["LOOPBLOOM_DEBUG_DATE"], "%Y-%m-%d")

    # Setup: Create a goal with a phase containing three ordered micro-habits
    runner.invoke(cli, ["goal", "add", "Fitness"])
    runner.invoke(cli, ["micro", "add", "Walk 5 min", "--goal", "Fitness", "--phase", "Phase 1"])
    runner.invoke(cli, ["micro", "add", "Walk 10 min", "--goal", "Fitness", "--phase", "Phase 1"])
    runner.invoke(cli, ["micro", "add", "Walk 15 min", "--goal", "Fitness", "--phase", "Phase 1"])

    # Verify data.json exists after initial commands
    assert data_path.exists()

    # Programmatically inject 12 successful check-ins (out of 14 days) for "Walk 5 min"
    with open(data_path, "r+") as f:
        data = json.load(f)
        goal = data[0]  # Assuming 'Fitness' is the first goal
        micro_goal = goal["phases"][0]["micro_goals"][0] # Assuming 'Walk 5 min' is the first micro-goal

        # Clear existing checkins to ensure a clean slate for injection
        micro_goal["checkins"] = []

        for i in range(14):
            checkin_date = fixed_today - timedelta(days=i) # Use fixed_today
            if i < 12: # Make 12 successful check-ins
                micro_goal["checkins"].append({
                    "date": checkin_date.date().isoformat(),
                    "success": True,
                    "note": ""
                })
            else: # Make 2 skipped check-ins
                micro_goal["checkins"].append({
                    "date": checkin_date.date().isoformat(),
                    "success": False,
                    "note": ""
                })
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    # Run summary and assert it suggests advancement.
    result = runner.invoke(cli, ["summary", "--goal", "Fitness"])
    assert result.exit_code == 0
    assert "Advance?" in result.output
    assert "Walk 5 min" in result.output # Assert that the current micro-habit is still active


def test_reports_handle_large_data_volume_gracefully(runner, setup_temp_data_path):
    """
    Test that reporting commands handle large data volumes gracefully.
    """
    data_path = setup_temp_data_path / "data.json"
    # Configure data path
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_path)])
    assert result.exit_code == 0

    # Setup: Programmatically create 10 goals, each with 5 micro-habits,
    # and generate hundreds of check-ins across a 90-day period.
    goals_data = []
    today = datetime.now()
    for i in range(10): # 10 goals
        goal_name = f"Goal {i+1}"
        goal = GoalArea(name=goal_name)
        phase = Phase(name="Phase 1")
        for j in range(5): # 5 micro-habits per goal
            micro_name = f"Micro {j+1}"
            micro = MicroGoal(name=micro_name)
            for k in range(90): # 90 days of check-ins
                checkin_date = today - timedelta(days=k)
                status = True if k % 2 == 0 else False # Alternate success/skip
                # Create Checkin instance
                checkin_instance = Checkin(date=checkin_date.date(), success=status, note="")
                micro.checkins.append(checkin_instance)
            phase.micro_goals.append(micro)
        goal.phases.append(phase)
        goals_data.append(json.loads(goal.model_dump_json())) # Use model_dump_json and json.loads

    with open(data_path, "w") as f:
        json.dump(goals_data, f, indent=2)

    # Action: Run report --mode calendar, report --mode success, and report --mode line.
    # Assertion: Assert that all commands complete successfully without errors and produce non-empty output.

    # report --mode calendar
    result = runner.invoke(cli, ["report", "--mode", "calendar"])
    assert result.exit_code == 0
    assert len(result.output) > 0
    assert "LoopBloom Check-in Heatmap – July 2025" in result.output

    # report --mode success
    result = runner.invoke(cli, ["report", "--mode", "success"])
    assert result.exit_code == 0
    assert len(result.output) > 0
    assert "Success Rates per Goal" in result.output

    # report --mode line
    result = runner.invoke(cli, ["report", "--mode", "line"])
    assert result.exit_code == 0
    assert len(result.output) > 0
    assert "Success Rate (Last 30 Days)" in result.output
