from __future__ import annotations

import click

from loopbloom.core import review as rv
from loopbloom.cli import ui


@click.command(name="review", help="Reflect on your progress.")
@click.option(
    "--period",
    default="day",
    help="Time period for the review (e.g., day or week).",
)
def review(period: str) -> None:
    """Interactive prompt that saves a review entry."""
    answer = click.prompt("What went well?")
    rv.add_entry(period=period, went_well=answer)
    ui.success("Review saved.")


review_cmd = review
