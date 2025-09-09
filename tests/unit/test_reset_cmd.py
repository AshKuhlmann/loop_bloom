import json

import pytest
from click.testing import CliRunner

from loopbloom.__main__ import cli
from loopbloom.core.models import GoalArea


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_temp_data_path(tmp_path, monkeypatch):
    # This fixture ensures each test gets a clean, isolated data directory
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))
    return tmp_path


def test_reset_command_confirms_and_deletes_data(runner, setup_temp_data_path):
    """
    Test that the reset command prompts for confirmation and deletes the data file.
    """
    data_file = setup_temp_data_path / "data.json"

    # Create a dummy data file
    with open(data_file, "w") as f:
        json.dump([GoalArea(name="Test Goal").model_dump(mode="json")], f)

    # Configure the CLI to use this data file
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_file)])
    assert result.exit_code == 0

    # Run the reset command, confirming with 'y'
    result = runner.invoke(cli, ["config", "reset"], input="y\n")

    assert (
        "This will delete all your LoopBloom data and goals. Are you sure?"
        in result.output
    )
    assert "Successfully deleted data at:" in result.output
    assert not data_file.exists()  # Assert that the data file is deleted
    assert result.exit_code == 0


def test_reset_command_can_be_skipped(runner, setup_temp_data_path):
    """
    Test that the reset command can be skipped by declining the confirmation.
    """
    data_file = setup_temp_data_path / "data.json"

    # Create a dummy data file
    with open(data_file, "w") as f:
        json.dump([GoalArea(name="Test Goal").model_dump(mode="json")], f)

    # Configure the CLI to use this data file
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_file)])
    assert result.exit_code == 0

    # Run the reset command, declining with 'n'
    result = runner.invoke(cli, ["config", "reset"], input="n\n")

    assert (
        "This will delete all your LoopBloom data and goals. Are you sure?"
        in result.output
    )
    assert "Reset cancelled." in result.output
    assert data_file.exists()  # Assert that the data file still exists
    assert result.exit_code == 0


def test_reset_command_with_yes_flag(runner, setup_temp_data_path):
    """
    Test that the reset command works with the --yes flag, skipping confirmation.
    """
    data_file = setup_temp_data_path / "data.json"

    # Create a dummy data file
    with open(data_file, "w") as f:
        json.dump([GoalArea(name="Test Goal").model_dump(mode="json")], f)

    # Configure the CLI to use this data file
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_file)])
    assert result.exit_code == 0

    # Run the reset command with --yes flag
    result = runner.invoke(cli, ["config", "reset", "--yes"])

    assert (
        "This will delete all your LoopBloom data and goals. Are you sure?"
        not in result.output
    )
    assert "Successfully deleted data at:" in result.output
    assert not data_file.exists()  # Assert that the data file is deleted
    assert result.exit_code == 0


def test_reset_command_no_data_found(runner, setup_temp_data_path):
    """
    Test that the reset command handles cases where no data file exists.
    """
    data_file = setup_temp_data_path / "non_existent_data.json"

    # Configure the CLI to use this non-existent data file
    result = runner.invoke(cli, ["config", "set", "data_path", str(data_file)])
    assert result.exit_code == 0

    # Run the reset command with --yes flag
    result = runner.invoke(cli, ["config", "reset", "--yes"])

    assert "No data found to reset." in result.output
    assert result.exit_code == 0
