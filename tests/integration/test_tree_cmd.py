"""Integration tests for the tree CLI command."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture()
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    """Return a CLI runner with the data path configured."""
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))
    return CliRunner()


class TestTreeCommand:
    def setup_method(self) -> None:
        """Reload and store the CLI for each test."""
        from loopbloom import __main__ as main

        self.cli = main.cli

    def test_tree_displays_hierarchy(self, runner: CliRunner) -> None:
        """Ensure tree output includes goal, phase, and micro names."""
        runner.invoke(self.cli, ["goal", "add", "Exercise"], catch_exceptions=False)
        runner.invoke(
            self.cli,
            ["goal", "phase", "add", "Exercise", "Base"],
            catch_exceptions=False,
        )
        runner.invoke(
            self.cli,
            [
                "micro",
                "add",
                "Walk",
                "--goal",
                "Exercise",
                "--phase",
                "Base",
            ],
            catch_exceptions=False,
        )

        res = runner.invoke(self.cli, ["tree"], catch_exceptions=False)
        assert "Exercise" in res.output
        assert "Base" in res.output
        assert "Walk" in res.output

    def test_tree_with_complex_hierarchy(self, runner: CliRunner) -> None:
        """Tests that the 'tree' command correctly displays a complex hierarchy of
        goals, phases, and micro-goals."""
        # Setup: Create a complex structure
        runner.invoke(self.cli, ["goal", "add", "Complex Goal"], catch_exceptions=False)
        runner.invoke(
            self.cli,
            ["goal", "phase", "add", "Complex Goal", "Phase 1"],
            catch_exceptions=False,
        )
        runner.invoke(
            self.cli,
            [
                "micro",
                "add",
                "Micro 1.1",
                "--goal",
                "Complex Goal",
                "--phase",
                "Phase 1",
            ],
            catch_exceptions=False,
        )
        runner.invoke(
            self.cli,
            [
                "micro",
                "add",
                "Micro 1.2",
                "--goal",
                "Complex Goal",
                "--phase",
                "Phase 1",
            ],
            catch_exceptions=False,
        )
        runner.invoke(
            self.cli,
            ["goal", "phase", "add", "Complex Goal", "Phase 2"],
            catch_exceptions=False,
        )
        runner.invoke(
            self.cli,
            [
                "micro",
                "add",
                "Micro 2.1",
                "--goal",
                "Complex Goal",
                "--phase",
                "Phase 2",
            ],
            catch_exceptions=False,
        )
        runner.invoke(
            self.cli,
            ["micro", "add", "Direct Micro", "--goal", "Complex Goal"],
            catch_exceptions=False,
        )
        runner.invoke(self.cli, ["goal", "add", "Simple Goal"], catch_exceptions=False)
        runner.invoke(
            self.cli,
            ["micro", "add", "Simple Micro", "--goal", "Simple Goal"],
            catch_exceptions=False,
        )

        # Action
        result = runner.invoke(self.cli, ["tree"], catch_exceptions=False)

        # Assert
        assert result.exit_code == 0
        output = result.output
        assert "Complex Goal" in output
        assert "Phase 1" in output
        assert "Micro 1.1" in output
        assert "Micro 1.2" in output
        assert "Phase 2" in output
        assert "Micro 2.1" in output
        assert "Direct Micro" in output
        assert "Simple Goal" in output
        assert "Simple Micro" in output
        # Check for tree structure characters
        assert "├──" in output
        assert "└──" in output
