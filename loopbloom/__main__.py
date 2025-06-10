"""LoopBloom CLI entry point."""

from typing import TYPE_CHECKING, cast

import click
from click import Command

from loopbloom.cli.checkin import checkin
from loopbloom.cli.cope import cope  # NEW
from loopbloom.cli.goal import goal
from loopbloom.cli.summary import summary

if TYPE_CHECKING:  # pragma: no cover - hints for mypy
    pass


@click.group()
def cli() -> None:
    """LoopBloom – tiny habits, big momentum."""
    pass


# Register sub-commands
cli.add_command(goal)
cli.add_command(cast(Command, checkin))  # type: ignore[redundant-cast]  # NEW
cli.add_command(summary)  # NEW
cli.add_command(cope)

if __name__ == "__main__":
    cli()
