"""Utility helpers for friendlier CLI error messages."""

from __future__ import annotations

from difflib import get_close_matches
from typing import Iterable

import click


def suggest_name(name: str, options: Iterable[str]) -> str | None:
    """Return a close match for ``name`` from ``options`` if available."""
    matches = get_close_matches(name, list(options), n=1)
    return matches[0] if matches else None


def goal_not_found(name: str, goals: Iterable[str]) -> None:
    """Print helpful message when a goal is missing."""
    click.echo(f"[red]Goal not found: \"{name}\".[/red]")
    match = suggest_name(name, goals)
    if match:
        click.echo(f"\nDid you mean \"{match}\"?")  # pragma: no cover
    click.echo("Run 'loopbloom goal list' to see your available goals.")
