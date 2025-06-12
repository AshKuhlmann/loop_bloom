import csv
from tests.integration.conftest import reload_modules


def test_gc_02_run_interactive_coping_plan(isolated_env):
    """(GC-02) Verify an interactive coping plan runs correctly."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]

    # Action: Run the 'overwhelmed' plan and provide answers via input
    # The expected questions are based on the content of 'overwhelmed.yml'
    input_text = "My inbox\nReview 5 emails\n"
    result = runner.invoke(
        cli,
        ["cope", "run", "overwhelmed"],
        input=input_text,
        env=env,
    )

    # Assertions
    assert result.exit_code == 0
    assert "Identify the biggest stressor" in result.output
    assert "Pick one micro-action" in result.output
    assert "action dispels anxiety" in result.output  # Final confirmation


def test_de_01_export_data_to_csv(isolated_env):
    """(DE-01) Verify data can be exported to a CSV file."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]
    tmp_path = isolated_env["data_path"].parent

    # Setup: Create some data to export
    runner.invoke(cli, ["goal", "add", "CSV Test"], env=env)
    runner.invoke(
        cli,
        ["checkin", "--goal", "CSV Test", "--status", "done"],
        env=env,
    )

    # Action
    export_path = tmp_path / "progress.csv"
    result = runner.invoke(
        cli,
        ["export", "--fmt", "csv", "--out", str(export_path)],
        env=env,
    )

    # Assertions
    assert result.exit_code == 0
    assert export_path.exists()

    # Verify content of CSV
    with open(export_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        assert "goal_name" in header or "goal" in header
        assert "status" in header or "success" in header
        first_row = next(reader)
        assert "CSV Test" in first_row
        assert "done" in first_row or "1" in first_row


def test_cf_02_switch_storage_backend(isolated_env):
    """(CF-02) Verify the storage backend can be switched to SQLite."""
    runner = isolated_env["runner"]
    cli = isolated_env["cli"]
    env = isolated_env["env"]
    tmp_path = isolated_env["data_path"].parent

    # Action 1: Set config to use sqlite
    result_config = runner.invoke(
        cli,
        ["config", "set", "storage", "sqlite"],
        env=env,
    )
    assert result_config.exit_code == 0

    # Action 2: Add a goal, which should now go to the sqlite DB
    # The environment needs to be updated to point to the new DB path
    sqlite_db_path = tmp_path / "data.db"
    env["LOOPBLOOM_DATA_PATH"] = str(sqlite_db_path)

    # We need to reload the modules so they pick up the new config
    cli = reload_modules()

    result_add = runner.invoke(cli, ["goal", "add", "Test SQLite"], env=env)
    assert result_add.exit_code == 0

    # Assertions
    assert sqlite_db_path.exists()  # The DB file should have been created

    # Verify JSON file was NOT touched
    json_path = tmp_path / "data.json"
    assert not json_path.exists()
