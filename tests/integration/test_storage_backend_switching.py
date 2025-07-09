import pytest
from click.testing import CliRunner

from loopbloom.cli.__main__ import cli
from loopbloom.core.models import GoalArea, MicroGoal, Phase


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_temp_data_path(tmp_path):
    # This fixture ensures each test gets a clean, isolated data directory
    return tmp_path


def run_workflow(runner, data_path, backend):
    # Configure storage backend
    result = runner.invoke(cli, ["config", "set", "storage", backend])
    assert result.exit_code == 0
    assert f"storage = '{backend}'" in result.output

    # Set data path for the current backend
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_path)])
    assert result.exit_code == 0

    # Workflow steps
    result = runner.invoke(cli, ["goal", "add", "My Goal"])
    assert result.exit_code == 0
    assert "Added goal: My Goal" in result.output

    result = runner.invoke(cli, ["micro", "add", "My Micro", "--goal", "My Goal"])
    assert result.exit_code == 0
    assert "Micro-habit added: My Micro" in result.output

    result = runner.invoke(cli, ["checkin", "My Goal", "--success"])
    assert result.exit_code == 0
    assert "Logged!" in result.output

    result = runner.invoke(cli, ["tree"])
    assert result.exit_code == 0
    assert "My Goal" in result.output
    assert "My Micro" in result.output

    result = runner.invoke(cli, ["summary"])
    assert result.exit_code == 0
    assert "My Goal" in result.output
    assert "My Micro" in result.output
    assert "1/1 (100 %)" in result.output  # Check success rate

    # Export data and verify content
    export_file = data_path / f"export_{backend}.json"
    result = runner.invoke(cli, ["export", "--fmt", "json", "--out", str(export_file)])
    assert result.exit_code == 0
    assert f"Exported data to {export_file}" in result.output
    assert export_file.exists()

    # Basic check of exported content (more detailed checks can be added if needed)
    exported_content = export_file.read_text()
    assert "My Goal" in exported_content
    assert "My Micro" in exported_content
    assert "checkins" in exported_content


def test_flow_works_identically_on_json_and_sqlite(runner, setup_temp_data_path):
    """
    Test that a full user workflow works identically for JSON and SQLite backends.
    """
    # Test with JSON backend
    json_data_path = setup_temp_data_path / "json_data"
    json_data_path.mkdir()
    run_workflow(runner, json_data_path, "json")

    # Test with SQLite backend
    sqlite_data_path = setup_temp_data_path / "sqlite_data"
    sqlite_data_path.mkdir()
    run_workflow(runner, sqlite_data_path, "sqlite")
