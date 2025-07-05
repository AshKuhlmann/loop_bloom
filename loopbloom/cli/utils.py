"""Utility helpers for friendlier CLI error messages."""

from __future__ import annotations

import logging
from difflib import get_close_matches
from typing import Iterable, Optional

import click

from loopbloom.core.models import GoalArea, Phase


def suggest_name(name: str, options: Iterable[str]) -> str | None:
    """Suggest the closest match for a given name.

    Args:
        name: The name entered by the user.
        options: Known valid options.

    Returns:
        The closest matching option or ``None`` when no close match exists.
    """
    # ``get_close_matches`` does fuzzy string comparison to help the user.
    matches = get_close_matches(name, list(options), n=1)
    return matches[0] if matches else None


def goal_not_found(name: str, goals: Iterable[str]) -> None:
    """Print a helpful error message when a goal cannot be found."""
    logger = logging.getLogger(__name__)
    logger.error("Goal not found: %s", name)
    click.echo(f'[red]Goal not found: "{name}".[/red]')
    # Suggest the closest existing goal to reduce user confusion.
    match = suggest_name(name, goals)
    if match:
        click.echo(f'\nDid you mean "{match}"?')  # pragma: no cover
    click.echo("Run 'loopbloom goal list' to see your available goals.")


def find_goal(goals: Iterable[GoalArea], name: str) -> Optional[GoalArea]:
    """Return the goal area whose name matches ``name``.

    Args:
        goals: Iterable of available goal areas.
        name: Name to search for (case-insensitive).

    Returns:
        The matching :class:`GoalArea` or ``None`` if not found.
    """
    return next((g for g in goals if g.name.lower() == name.lower()), None)


def find_phase(goal: GoalArea, name: str) -> Optional[Phase]:
    """Return the phase within ``goal`` whose name matches ``name``.

    Args:
        goal: Parent goal area.
        name: Phase name to search for.

    Returns:
        The matching :class:`Phase` or ``None`` if not found.
    """
    return next(
        (p for p in goal.phases if p.name.lower() == name.lower()),
        None,
    )


def get_goal_from_name(name: str) -> Optional[GoalArea]:
    """Load and return the goal matching ``name`` from the current store.

    Args:
        name: Goal name to search for.

    Returns:
        The :class:`GoalArea` when found, otherwise ``None``.
    """
    store = click.get_current_context().obj
    goals = store.load()
    return next((g for g in goals if g.name.lower() == name.lower()), None)


def save_goal(goal: GoalArea) -> None:
    """Persist ``goal`` using the current store.

    Args:
        goal: Goal to save.
    """
    store = click.get_current_context().obj
    store.save_goal_area(goal)
