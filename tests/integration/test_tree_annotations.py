from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner


@pytest.fixture()
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(tmp_path / "data.json"))
    return CliRunner()


class TestTreeAnnotations:
    def setup_method(self) -> None:
        from loopbloom import __main__ as main

        self.cli = main.cli

    def _seed(self, runner: CliRunner) -> None:
        runner.invoke(self.cli, ["goal", "add", "G"], catch_exceptions=False)
        # Active (default)
        runner.invoke(
            self.cli, ["micro", "add", "A", "--goal", "G"], catch_exceptions=False
        )
        # Complete
        runner.invoke(
            self.cli, ["micro", "add", "B", "--goal", "G"], catch_exceptions=False
        )
        runner.invoke(
            self.cli, ["micro", "complete", "B", "--goal", "G"], catch_exceptions=False
        )
        # Cancelled
        runner.invoke(
            self.cli, ["micro", "add", "C", "--goal", "G"], catch_exceptions=False
        )
        runner.invoke(
            self.cli, ["micro", "cancel", "C", "--goal", "G"], catch_exceptions=False
        )

    def test_tree_shows_unicode_glyphs(self, runner: CliRunner) -> None:
        self._seed(runner)
        res = runner.invoke(self.cli, ["tree"], catch_exceptions=False)
        assert res.exit_code == 0
        out = res.output
        assert "✓ A" in out
        assert "✔ B" in out
        assert "✖ C" in out

    def test_tree_ascii_flag_fallback(self, runner: CliRunner) -> None:
        self._seed(runner)
        res = runner.invoke(self.cli, ["tree", "--ascii"], catch_exceptions=False)
        assert res.exit_code == 0
        out = res.output
        assert "* A" in out
        assert "v B" in out
        assert "x C" in out
