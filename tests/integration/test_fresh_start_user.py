import pytest
from click.testing import CliRunner
from pathlib import Path
import json
from datetime import datetime, timedelta

import os
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
    with runner.isolated_filesystem():
        data_file = setup_temp_data_path / "data.json"
        export_file = setup_temp_data_path / "exported_data.json"

        # Set environment variable before importing cli
        os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
        import loopbloom.__main__
        cli = loopbloom.__main__.cli

        # Create data.json directly with two goals
        initial_goals = [
            {
                "id": "fitness-id",
                "name": "Fitness",
                "notes": None,
                "phases": [],
                "micro_goals": []
            },
            {
                "id": "learning-id",
                "name": "Learning",
                "notes": None,
                "phases": [],
                "micro_goals": []
            }
        ]
        with open(data_file, "w") as f:
            json.dump(initial_goals, f, indent=2)

        # 3. Use the export command to save the current state to a JSON file.
        result = runner.invoke(cli, ["export", "--fmt", "json", "--out", str(export_file)])
        assert result.exit_code == 0
        assert str(export_file) in result.output
        assert export_file.exists()

        assert export_file.exists()

        # 4. Verify that the exported JSON file contains the correct data.
        with open(export_file, "r") as f:
            exported_data = json.load(f)

        assert len(exported_data) == 2 # Fitness and Learning goals
        fitness_goal = next((g for g in exported_data if g["name"] == "Fitness"), None)
        learning_goal = next((g for g in exported_data if g["name"] == "Learning"), None)

        assert fitness_goal is not None
        assert learning_goal is not None

        del os.environ["LOOPBLOOM_DATA_PATH"]

    
