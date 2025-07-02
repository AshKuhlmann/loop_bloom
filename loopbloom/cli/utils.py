"""Utility helpers for friendlier CLI error messages."""

from __future__ import annotations

from difflib import get_close_matches
from typing import Iterable

import click
import logging


def suggest_name(name: str, options: Iterable[str]) -> str | None:
    """Return a close match for ``name`` from ``options`` if available."""
    # ``get_close_matches`` does fuzzy string comparison to help the user.
    matches = get_close_matches(name, list(options), n=1)
    return matches[0] if matches else None


def goal_not_found(name: str, goals: Iterable[str]) -> None:
    """Print helpful message when a goal is missing."""
    logger = logging.getLogger(__name__)
    logger.error("Goal not found: %s", name)
    click.echo(f"[red]Goal not found: \"{name}\".[/red]")
    # Suggest the closest existing goal to reduce user confusion.
    match = suggest_name(name, goals)
    if match:
        click.echo(f"\nDid you mean \"{match}\"?")  # pragma: no cover
    click.echo("Run 'loopbloom goal list' to see your available goals.")
