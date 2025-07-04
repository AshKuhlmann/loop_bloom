"""Add free-form journal entries."""

from __future__ import annotations

import logging

import click

from loopbloom.core import journal as jr

logger = logging.getLogger(__name__)


@click.command(name="journal", help="Record a journal entry.")
@click.argument("text")
@click.option(
    "--goal",
    "goal_name",
    default=None,
    help="Tag entry with a goal.",
)
def journal(text: str, goal_name: str | None) -> None:
    """Save ``text`` as a journal entry optionally linked to ``goal_name``."""
    logger.info(
        "Adding journal entry%s",
        f" for {goal_name}" if goal_name else "",
    )
    jr.add_entry(text, goal_name)
    click.echo("[green]Entry saved.")
