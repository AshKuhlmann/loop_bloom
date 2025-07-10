import pytest
from click.testing import CliRunner

from loopbloom.__main__ import cli
from loopbloom.core.models import GoalArea, MicroGoal, Phase


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def setup_goals(tmp_path, monkeypatch):
    # Setup a temporary data.json for testing
    data_path = tmp_path / "data.json"
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(data_path))
    monkeypatch.setenv("LOOPBLOOM_STORAGE_BACKEND", "json")
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Create two goals with active micro-habits
        runner.invoke(cli, ["goal", "add", "Exercise"])
        runner.invoke(cli, ["micro", "add", "Run 30 min", "--goal", "Exercise"])
        runner.invoke(cli, ["goal", "add", "Reading"])
        runner.invoke(cli, ["micro", "add", "Read 10 pages", "--goal", "Reading"])
    return data_path


def test_checkin_without_goal_triggers_interactive_prompt(runner, setup_goals):
    """
    Test that running 'checkin' without a goal name triggers an interactive prompt
    and presents a list of active micro-habits.
    """
    result = runner.invoke(cli, ["checkin"], input="1\n")  # Select the first option
    assert "Which goal do you want to check in for?" in result.output
    assert "Exercise" in result.output
    assert "Reading" in result.output
    assert "Run 30 min" in result.output or "Read 10 pages" in result.output
    assert result.exit_code == 0


def test_goal_rm_without_name_triggers_prompt(runner, setup_goals):
    """
    Test that running 'goal rm' without a goal name prompts the user to select
    which goal to delete.
    """
    result = runner.invoke(cli, ["goal", "rm"], input="1\ny\n")  # Select the first option and confirm deletion
    assert "Which goal do you want to delete?" in result.output
    assert "Exercise" in result.output
    assert "Reading" in result.output
    assert result.exit_code == 0


def test_command_with_typo_suggests_correction(runner, setup_goals):
    """
    Test that a command with a typo in the goal name suggests the correct name.
    """
    result = runner.invoke(cli, ["checkin", "Exersise", "--success"])
    assert 'Goal not found: "Exersise".' in result.output
    assert 'Did you mean "Exercise"?' in result.output
    assert result.exit_code != 0
