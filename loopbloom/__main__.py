"""LoopBloom CLI entry point."""

import click

from loopbloom.cli.goal import goal


@click.group()
def cli() -> None:
    """LoopBloom – tiny habits, big momentum."""
    pass


# Register sub-commands
cli.add_command(goal)

if __name__ == "__main__":
    cli()
