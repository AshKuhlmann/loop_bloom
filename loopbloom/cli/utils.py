"""Utility helpers for friendlier CLI error messages."""

from __future__ import annotations

from difflib import get_close_matches
from typing import Iterable, Optional

from loopbloom.core.models import GoalArea, Phase

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


def find_goal(goals: Iterable[GoalArea], name: str) -> Optional[GoalArea]:
    """Return the goal area whose name matches ``name``."""
    return next((g for g in goals if g.name.lower() == name.lower()), None)


def find_phase(goal: GoalArea, name: str) -> Optional[Phase]:
    """Return the phase within ``goal`` whose name matches ``name``."""
    return next((p for p in goal.phases if p.name.lower() == name.lower()), None)

