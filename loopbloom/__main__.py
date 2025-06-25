"""LoopBloom CLI entry point."""

import os
from typing import TYPE_CHECKING, cast

import click
from click import Command

from loopbloom.cli.checkin import checkin
from loopbloom.cli.config import config  # NEW
from loopbloom.cli.cope import cope  # NEW
from loopbloom.cli.export import export  # NEW
from loopbloom.cli.goal import goal
from loopbloom.cli.micro import micro
from loopbloom.cli.report import report
from loopbloom.cli.summary import summary
from loopbloom.cli.tree import tree
from loopbloom.core import config as cfg
from loopbloom.storage.base import Storage
from loopbloom.storage.json_store import (
    DEFAULT_PATH as JSON_DEFAULT_PATH,
)
from loopbloom.storage.json_store import (
    JSONStore,
)
from loopbloom.storage.sqlite_store import (
    DEFAULT_PATH as SQLITE_DEFAULT_PATH,
)
from loopbloom.storage.sqlite_store import (
    SQLiteStore,
)

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
        # Allow ``LOOPBLOOM_SQLITE_PATH`` to override the on-disk location.
        path = os.getenv("LOOPBLOOM_SQLITE_PATH", str(SQLITE_DEFAULT_PATH))
        store = SQLiteStore(path)
    else:
        # Default to a JSON file if no storage override is set. ``LOOPBLOOM_DATA_PATH``
        # lets advanced users keep data elsewhere.
        path = os.getenv("LOOPBLOOM_DATA_PATH", str(JSON_DEFAULT_PATH))
        store = JSONStore(path)

    # Expose the store instance to subcommands via Click's context object.
    ctx.obj = store


# Register sub-commands so ``loopbloom`` becomes a multi-command CLI.
# Individual commands are kept in separate modules for clarity and to
# encourage contribution. Order here controls help output ordering.
cli.add_command(goal)
cli.add_command(cast(Command, checkin))  # type: ignore[redundant-cast]  # NEW
cli.add_command(summary)  # NEW
cli.add_command(report)
cli.add_command(cope)
cli.add_command(config)
cli.add_command(export)
cli.add_command(tree)
cli.add_command(micro)

if __name__ == "__main__":
    cli()
