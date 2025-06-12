import json


def test_hg_01_add_new_goal(isolated_env):
    """(HG-01) Verify a new goal can be added."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]
    data_path = isolated_env["data_path"]

    result = runner.invoke(cli, ["goal", "add", "Sleep Hygiene"], env=env)

    assert result.exit_code == 0
    assert "Added goal: Sleep Hygiene" in result.output
    # Verify the data was written to the store
    data = json.loads(data_path.read_text())
    assert len(data) == 1
    assert data[0]["name"] == "Sleep Hygiene"


def test_hg_02_list_existing_goals(isolated_env):
    """(HG-02) Verify existing goals are listed correctly."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]

    # First, add a goal to list
    runner.invoke(cli, ["goal", "add", "Sleep Hygiene"], env=env)

    # Now, list it
    result = runner.invoke(cli, ["goal", "list"], env=env)
    assert result.exit_code == 0
    assert "Sleep Hygiene" in result.output


def test_hg_06_add_micro_habit(isolated_env):
    """(HG-06) Verify a micro-habit can be added to a goal and phase."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]
    data_path = isolated_env["data_path"]

    # Setup: Create goal and phase
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "phase", "add", "Exercise", "Cardio"], env=env)

    # Action: Add micro-habit
    result = runner.invoke(
        cli,
        ["goal", "micro", "add", "Exercise", "Cardio", "Walk for 5 minutes"],
        env=env,
    )

    # Assertions
    assert result.exit_code == 0
    assert "Added micro-habit" in result.output
    data = json.loads(data_path.read_text())
    assert (
        data[0]["phases"][0]["micro_goals"][0]["name"]
        == "Walk for 5 minutes"
    )
