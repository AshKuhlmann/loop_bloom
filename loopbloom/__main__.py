"""LoopBloom CLI entry point."""

from typing import TYPE_CHECKING, cast

import os

import click
from click import Command

from loopbloom.cli.checkin import checkin
from loopbloom.cli.config import config  # NEW
from loopbloom.cli.cope import cope  # NEW
from loopbloom.cli.export import export  # NEW
from loopbloom.cli.goal import goal
from loopbloom.cli.micro import micro
from loopbloom.cli.summary import summary
from loopbloom.cli.tree import tree
from loopbloom.core import config as cfg
from loopbloom.storage.json_store import (
    JSONStore,
    DEFAULT_PATH as JSON_DEFAULT_PATH,
)
from loopbloom.storage.sqlite_store import (
    SQLiteStore,
    DEFAULT_PATH as SQLITE_DEFAULT_PATH,
)
from loopbloom.storage.base import Storage

if TYPE_CHECKING:  # pragma: no cover - hints for mypy
    pass


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """LoopBloom – tiny habits, big momentum."""
    config = cfg.load()
    storage_type = config.get("storage", "json")

    store: Storage
    if storage_type == "sqlite":
        path = os.getenv("LOOPBLOOM_SQLITE_PATH", str(SQLITE_DEFAULT_PATH))
        store = SQLiteStore(path)
    else:
        path = os.getenv("LOOPBLOOM_DATA_PATH", str(JSON_DEFAULT_PATH))
        store = JSONStore(path)

    ctx.obj = store


# Register sub-commands
cli.add_command(goal)
cli.add_command(cast(Command, checkin))  # type: ignore[redundant-cast]  # NEW
cli.add_command(summary)  # NEW
cli.add_command(cope)
cli.add_command(config)
cli.add_command(export)
cli.add_command(tree)
cli.add_command(micro)

if __name__ == "__main__":
    cli()
