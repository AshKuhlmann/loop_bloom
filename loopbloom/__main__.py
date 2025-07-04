"""LoopBloom CLI entry point.

This module wires together all subcommands and selects the appropriate
storage backend based on the user's configuration.
"""

import logging
import os
from typing import TYPE_CHECKING, cast

import click
from click import Command

from loopbloom.cli.backup import backup  # NEW
from loopbloom.cli.checkin import checkin
from loopbloom.cli.config import config  # NEW
from loopbloom.cli.cope import cope  # NEW
from loopbloom.cli.export import export  # NEW
from loopbloom.cli.goal import goal
from loopbloom.cli.journal import journal
from loopbloom.cli.micro import micro
from loopbloom.cli.pause import pause
from loopbloom.cli.report import report
from loopbloom.cli.review import review
from loopbloom.cli.summary import summary
from loopbloom.cli.tree import tree
from loopbloom.core import config as cfg
from loopbloom.logging import setup_logging
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
@click.option("--verbose", is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """LoopBloom – tiny habits, big momentum."""
    # Load user configuration to determine which storage backend to use.
    setup_logging(level=logging.DEBUG if verbose else logging.INFO)

    config = cfg.load()
    storage_type = config.get("storage", "json")
    cfg_path = str(config.get("data_path") or "")

    store: Storage
    if storage_type == "sqlite":
        # Environment variable overrides config which overrides the default.
        sqlite_env = os.getenv("LOOPBLOOM_SQLITE_PATH")
        path = sqlite_env or cfg_path or str(SQLITE_DEFAULT_PATH)
        store = SQLiteStore(path)
    else:
        # ``LOOPBLOOM_DATA_PATH`` or config ``data_path`` may override.
        data_env = os.getenv("LOOPBLOOM_DATA_PATH")
        path = data_env or cfg_path or str(JSON_DEFAULT_PATH)
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
cli.add_command(backup)
cli.add_command(tree)
cli.add_command(micro)
cli.add_command(journal)
cli.add_command(review)
cli.add_command(pause)

if __name__ == "__main__":
    cli()
