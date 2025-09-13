"""Unified terminal UI helpers using Rich.

This module centralizes console configuration and provides small helper
functions for common message types so CLI commands can produce consistent,
readable output with or without color (depending on TTY and NO_COLOR).
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from rich.console import Console


def _make_console() -> Console:
    """Return a configured Rich Console.

    - Disables color automatically when stdout is not a TTY or when the
      standard ``NO_COLOR`` env var is present.
    - Leaves markup enabled so commands can pass simple markup if needed.
    """
    no_color_env = os.getenv("NO_COLOR") is not None
    is_tty = sys.stdout.isatty()
    # If not a TTY or NO_COLOR is set, disable color. Otherwise let Rich
    # use terminal detection to enable styling.
    return Console(no_color=(no_color_env or not is_tty))


console: Console = _make_console()


def configure(*, no_color: Optional[bool] = None) -> None:
    """Reconfigure the global console.

    Args:
        no_color: If provided, force-disable color regardless of TTY/NO_COLOR.

    This lets the top-level CLI pass a `--no-color/--plain` flag to ensure
    deterministic output during tests or when users prefer plain text.
    """
    global console
    if no_color is None:
        console = _make_console()
    else:
        console = Console(no_color=bool(no_color))


def _print(msg: str) -> None:
    """Internal print that respects console settings."""
    console.print(msg)


def success(msg: str) -> None:
    """Print a success message in green with a checkmark."""
    _print(f"[green]✓ {msg}[/green]")


def warn(msg: str) -> None:
    """Print a warning message in yellow."""
    _print(f"[yellow]{msg}[/yellow]")


def error(msg: str) -> None:
    """Print an error message in red."""
    _print(f"[red]{msg}[/red]")


def info(msg: str) -> None:
    """Print an informational message (dim)."""
    _print(f"[dim]{msg}[/dim]")


def header(text: str, *, icon: Optional[str] = None) -> None:
    """Print a bold section header optionally prefixed by an icon."""
    prefix = f"{icon} " if icon else ""
    _print(f"[bold]{prefix}{text}[/bold]")
