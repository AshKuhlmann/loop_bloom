from datetime import datetime, timedelta
import json


def create_checkin_history(data_path, goal_name, micro_goal_name, success_days, total_days):
    """Helper to create fake check-in data for progression tests."""
    checkins = []
    today = datetime.now().date()
    for i in range(total_days):
        date = today - timedelta(days=i)
        status = "done" if i < success_days else "skip"
        checkins.append({
            "goal_name": goal_name,
            "micro_goal_name": micro_goal_name,
            "timestamp": date.isoformat(),
            "status": status,
            "note": "fake history"
        })
    # This is a simplified representation; the actual data structure might be nested
    # For this test, we assume a flat list of check-ins at the top level of the JSON
    # A more robust helper would interact with the application's data models.
    with open(data_path, "r+") as f:
        data = json.load(f)
        if "checkins" not in data[0]:
            data[0]["checkins"] = []
        data[0]["checkins"].extend(checkins)
        f.seek(0)
        json.dump(data, f)


def test_ci_01_successful_checkin(isolated_env):
    """(CI-01) Verify a 'done' check-in logs correctly and gives positive feedback."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]

    # Setup
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "micro", "add", "Exercise", "default", "Walk for 5 minutes"], env=env)

    # Action
    result = runner.invoke(cli, ["checkin", "--goal", "Exercise", "--status", "done", "--note", "Felt great!"], env=env)

    # Assertions
    assert result.exit_code == 0
    assert "Your consistency is paying off" in result.output or "🎉" in result.output


def test_sp_02_summary_triggers_progression(isolated_env):
    """(SP-02) Verify summary triggers advancement prompt with high success rate."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]
    data_path = isolated_env["data_path"]

    # Setup: Create a goal and a history of high success
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "micro", "add", "Exercise", "default", "Walk for 5 minutes"], env=env)
    create_checkin_history(data_path, "Exercise", "Walk for 5 minutes", success_days=12, total_days=14)

    # Action
    result = runner.invoke(cli, ["summary"], env=env)

    # Assertions
    assert result.exit_code == 0
    assert "Advance?" in result.output
    assert "(86 %" in result.output  # 12/14 is approx 86%


def test_sp_03_accepting_advancement(isolated_env):
    """(SP-03) Verify user can accept a progression suggestion."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]
    data_path = isolated_env["data_path"]

    # Setup
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "micro", "add", "Exercise", "default", "Walk 5 min"], env=env)
    create_checkin_history(data_path, "Exercise", "Walk 5 min", success_days=13, total_days=14)

    # Action: Run summary and pipe "Y" to the input prompt
    result = runner.invoke(cli, ["summary", "--goal", "Exercise"], input="Y\n", env=env)

    # Assertions
    assert result.exit_code == 0
    assert "Advancing habit" in result.output or "Habit advanced" in result.output

    # Verify the micro-habit was actually updated in the data store
    data = json.loads(data_path.read_text())
    # Assuming the progression logic suggests "Walk 6 min"
    assert any("Walk 6 min" in mg["name"] for mg in data[0]["phases"][0]["micro_goals"])
