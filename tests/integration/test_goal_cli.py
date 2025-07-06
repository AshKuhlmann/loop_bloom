"""Integration tests for the goal CLI."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture()
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    """Return a CLI runner with the data path configured."""
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))
    return CliRunner()


def test_goal_phase_micro_crud(tmp_path):
    """End-to-end CRUD interactions via the CLI."""
    runner = CliRunner()
    # Use an isolated JSON path
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    if data_file.exists():
        data_file.unlink()

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    from loopbloom import __main__ as main

    cli = main.cli

    # Add a goal
    res = runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    assert res.exit_code == 0 and "Added goal:" in res.output

    # List goals
    res = runner.invoke(cli, ["goal", "list"], env=env)
    assert "Exercise" in res.output

    # Add phase
    res = runner.invoke(
        cli,
        ["goal", "phase", "add", "Exercise", "Foundation"],
        env=env,
    )
    assert res.exit_code == 0

    # Add micro-habit
    res = runner.invoke(
        cli,
        [
            "micro",
            "add",
            "Walk 5 min",
            "--goal",
            "Exercise",
            "--phase",
            "Foundation",
        ],
        env=env,
    )
    assert "Added micro-habit" in res.output

    # Cancel micro-habit
    res = runner.invoke(
        cli,
        [
            "micro",
            "rm",
            "Walk 5 min",
            "--goal",
            "Exercise",
            "--phase",
            "Foundation",
            "--yes",
        ],
        env=env,
    )
    assert "Deleted micro-habit" in res.output

    # Verify JSON structure saved
    data = json.loads(data_file.read_text())
    assert data[0]["phases"][0]["micro_goals"] == []


def test_goal_rm_missing(tmp_path) -> None:
    """Attempting to remove an unknown goal shows an error."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    from loopbloom import __main__ as main

    cli = main.cli

    res = runner.invoke(cli, ["goal", "rm", "Ghost", "--yes"], env=env)
    assert "Goal not found" in res.output


def test_phase_add_missing_goal(tmp_path) -> None:
    """Adding a phase to a nonexistent goal yields an error message."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    from loopbloom import __main__ as main

    cli = main.cli

    res = runner.invoke(
        cli,
        ["goal", "phase", "add", "Ghost", "Base"],
        env=env,
    )
    assert "[red]Goal not found" in res.output


def test_phase_rm(tmp_path) -> None:
    """Removing a phase deletes it from the goal."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    from loopbloom import __main__ as main

    cli = main.cli

    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "phase", "add", "Exercise", "Base"], env=env)

    res = runner.invoke(
        cli,
        ["goal", "phase", "rm", "Exercise", "Base", "--yes"],
        env=env,
    )
    assert "Deleted phase" in res.output

    data = json.loads(data_file.read_text())
    assert data[0]["phases"] == []


def test_micro_add_creates_phase(tmp_path) -> None:
    """Adding a micro-habit with a new phase creates that phase."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)

    from loopbloom import __main__ as main

    cli = main.cli

    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)

    res = runner.invoke(
        cli,
        [
            "micro",
            "add",
            "Walk",
            "--goal",
            "Exercise",
            "--phase",
            "Base",
        ],
        env=env,
    )
    assert "Added micro-habit" in res.output

    data = json.loads(data_file.read_text())
    assert len(data[0]["phases"]) == 1
    assert data[0]["phases"][0]["micro_goals"][0]["name"] == "Walk"


def test_goal_and_phase_notes(tmp_path) -> None:
    """Notes can be added and viewed for goals and phases."""
    runner = CliRunner()
    data_file = tmp_path / "data.json"
    env = {"LOOPBLOOM_DATA_PATH": str(data_file)}

    os.environ["LOOPBLOOM_DATA_PATH"] = str(data_file)
    from loopbloom import __main__ as main

    cli = main.cli

    # Goal notes
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    script = tmp_path / "edit_goal.sh"
    script.write_text("#!/bin/sh\necho 'start' > \"$1\"\n")
    script.chmod(0o755)
    runner.invoke(
        cli, ["goal", "notes", "Exercise"], env={**env, "EDITOR": str(script)}
    )
    res = runner.invoke(
        cli, ["goal", "notes", "Exercise"], env={**env, "EDITOR": "cat"}
    )
    assert "start" in res.output

    script.write_text("#!/bin/sh\necho 'updated' > \"$1\"\n")
    runner.invoke(
        cli, ["goal", "notes", "Exercise"], env={**env, "EDITOR": str(script)}
    )
    res = runner.invoke(
        cli, ["goal", "notes", "Exercise"], env={**env, "EDITOR": "cat"}
    )
    assert "updated" in res.output

    # Phase notes
    runner.invoke(cli, ["goal", "phase", "add", "Exercise", "Base"], env=env)
    script_p = tmp_path / "edit_phase.sh"
    script_p.write_text("#!/bin/sh\necho 'plan' > \"$1\"\n")
    script_p.chmod(0o755)
    runner.invoke(
        cli,
        ["goal", "phase", "notes", "Exercise", "Base"],
        env={**env, "EDITOR": str(script_p)},
    )
    res = runner.invoke(
        cli,
        ["goal", "phase", "notes", "Exercise", "Base"],
        env={**env, "EDITOR": "cat"},
    )
    assert "plan" in res.output

    script_p.write_text("#!/bin/sh\necho 'do it' > \"$1\"\n")
    runner.invoke(
        cli,
        ["goal", "phase", "notes", "Exercise", "Base"],
        env={**env, "EDITOR": str(script_p)},
    )
    res = runner.invoke(
        cli,
        ["goal", "phase", "notes", "Exercise", "Base"],
        env={**env, "EDITOR": "cat"},
    )
    assert "do it" in res.output


class TestGoalCLI:
    def setup_method(self) -> None:
        """Reload and store the CLI for each test."""
        from loopbloom import __main__ as main

        self.cli = main.cli

    def test_goal_notes_with_empty_input(
        self,
        runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Tests that 'goal notes' handles empty input from the editor correctly."""
        # Setup: Create a goal
        runner.invoke(
            self.cli,
            ["goal", "add", "Goal for Empty Notes"],
            catch_exceptions=False,
        )

        # Mock the editor to return an empty string
        script = tmp_path / "empty_notes.sh"
        script.write_text('#!/bin/sh\n: > "$1"\n')
        script.chmod(0o755)
        monkeypatch.setenv("EDITOR", str(script))

        # Action: Edit notes
        runner.invoke(
            self.cli,
            ["goal", "notes", "Goal for Empty Notes"],
            catch_exceptions=False,
        )

        # Assert: Check that the notes are empty
        result = runner.invoke(
            self.cli,
            ["goal", "notes", "Goal for Empty Notes"],
            catch_exceptions=False,
            env={"EDITOR": "cat"},
        )
        assert result.output.strip() in {"", "None"}

    def test_phase_notes_with_multiline_input(
        self,
        runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Tests that 'phase notes' correctly saves and displays multi-line notes."""
        # Setup: Create a goal and a phase
        runner.invoke(
            self.cli,
            ["goal", "add", "Goal for Multiline"],
            catch_exceptions=False,
        )
        runner.invoke(
            self.cli,
            ["goal", "phase", "add", "Goal for Multiline", "Phase for Multiline"],
            catch_exceptions=False,
        )

        # Mock the editor to return a multi-line string
        multiline_notes = "First line of notes.\nSecond line."
        script = tmp_path / "multiline_notes.sh"
        script.write_text(
            "#!/bin/sh\nprintf '%s' > \"$1\"\n" % multiline_notes.replace("\n", "\\n")
        )
        script.chmod(0o755)
        monkeypatch.setenv("EDITOR", str(script))

        # Action: Edit phase notes
        runner.invoke(
            self.cli,
            ["goal", "phase", "notes", "Goal for Multiline", "Phase for Multiline"],
            catch_exceptions=False,
        )

        # Assert: Check that the multi-line notes are displayed correctly
        result = runner.invoke(
            self.cli,
            [
                "goal",
                "phase",
                "notes",
                "Goal for Multiline",
                "Phase for Multiline",
            ],
            catch_exceptions=False,
            env={"EDITOR": "cat"},
        )
        assert "First line of notes." in result.output
        assert "Second line." in result.output
