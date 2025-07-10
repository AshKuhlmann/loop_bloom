import pytest
from click.testing import CliRunner
import os
# from loopbloom.__main__ import cli # Remove top-level import
from loopbloom.core.models import GoalArea, MicroGoal, Phase


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_temp_data_path(tmp_path, monkeypatch):
    # This fixture ensures each test gets a clean, isolated data directory
    return tmp_path


def _run_common_workflow(runner, data_path, backend):
    import os
    from loopbloom.__main__ import cli # Import cli here to ensure it picks up env vars

    # Configure storage backend (this will use the cli initialized with env vars)
    result = runner.invoke(cli, ["config", "set", "storage", backend])
    assert result.exit_code == 0
    assert "[green]Saved." in result.output

    # Set data path for the current backend
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_path / f"data.{'db' if backend == 'sqlite' else 'json'}")])
    assert result.exit_code == 0

    # Workflow steps
    result = runner.invoke(cli, ["goal", "add", "My Goal"])
    assert result.exit_code == 0
    assert "[green]Added goal:[/] My Goal" in result.output

    result = runner.invoke(cli, ["micro", "add", "My Micro", "--goal", "My Goal"])
    assert result.exit_code == 0
    assert "[green]Added micro-habit 'My Micro' to goal 'My Goal'" in result.output

    result = runner.invoke(cli, ["checkin", "My Goal", "--success"])
    assert result.exit_code == 0
    assert "✓" in result.output
    assert "Desktop notify failed" in result.output

    result = runner.invoke(cli, ["tree"])
    assert result.exit_code == 0
    assert "My Goal" in result.output
    assert "My Micro" in result.output

    result = runner.invoke(cli, ["summary"])
    assert result.exit_code == 0
    assert "My Goal" in result.output
    assert "LoopBloom Progress (last 14\xa0days)" in result.output

    # Export data and verify content
    export_file = data_path / f"export_{backend}.json"
    result = runner.invoke(cli, ["export", "--fmt", "json", "--out", str(export_file)])
    assert result.exit_code == 0
    assert f"[green]Exported JSON → {export_file}" in result.output
    assert export_file.exists()

    # Basic check of exported content (more detailed checks can be added if needed)
    exported_content = export_file.read_text()
    assert "My Goal" in exported_content
    assert "My Micro" in exported_content
    assert "checkins" in exported_content


def test_flow_works_with_json_backend(runner, setup_temp_data_path, monkeypatch):
    """
    Test that a full user workflow works correctly with the JSON backend.
    """
    json_data_path = setup_temp_data_path / "json_data"
    json_data_path.mkdir()
    
    # Set environment variables for JSON backend before cli is used
    monkeypatch.setenv("LOOPBLOOM_STORAGE_BACKEND", "json")
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(json_data_path / "data.json"))
    
    _run_common_workflow(runner, json_data_path, "json")


def test_flow_works_with_sqlite_backend(runner, setup_temp_data_path, monkeypatch):
    """
    Test that a full user workflow works correctly with the SQLite backend.
    """
    sqlite_data_path = setup_temp_data_path / "sqlite_data"
    sqlite_data_path.mkdir()

    # Set environment variables for SQLite backend before cli is used
    monkeypatch.setenv("LOOPBLOOM_STORAGE_BACKEND", "sqlite")
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(sqlite_data_path / "data.db"))
    
    _run_common_workflow(runner, sqlite_data_path, "sqlite")
