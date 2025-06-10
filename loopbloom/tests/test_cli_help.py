"""Smoke tests for the CLI entry point."""

from __future__ import annotations

import subprocess
import sys


def test_cli_help() -> None:
    """Ensure ``--help`` exits cleanly."""
    result = subprocess.run(
        [sys.executable, "-m", "loopbloom", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
