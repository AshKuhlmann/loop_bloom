"""LoopBloom CLI entry point.

This module wires together all subcommands and selects the appropriate
storage backend based on the user's configuration.
"""

import importlib
import logging
import os
import pkgutil
from typing import TYPE_CHECKING

import click

from loopbloom import cli as cli_package
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


class AppContext:
    """Object passed via Click context to hold global flags and store."""

    def __init__(
        self, store: Storage, *, debug: bool = False, dry_run: bool = False
    ) -> None:
        self.store = store
        self.debug = debug
        self.dry_run = dry_run


if TYPE_CHECKING:  # pragma: no cover - hints for mypy
    pass


def register_commands() -> None:
    """Dynamically discover and register all click commands."""
    package_path = cli_package.__path__
    prefix = cli_package.__name__ + "."
    for _, name, _ in pkgutil.iter_modules(package_path, prefix):
        module = importlib.import_module(name)
        for item in dir(module):
            if item.endswith("_cmd"):
                cmd_obj = getattr(module, item)
                if isinstance(cmd_obj, click.Command):
                    cli.add_command(cmd_obj)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose logging.")
@click.option(
    "--dry-run", is_flag=True, help="Simulate commands without saving changes."
)
@click.pass_context
def cli(ctx: click.Context, debug: bool, dry_run: bool) -> None:
    """LoopBloom – tiny habits, big momentum."""
    register_commands()
    setup_logging(level=logging.DEBUG if debug else logging.INFO)
    if debug:
        logging.getLogger().debug("Debug mode is ON")
        click.echo("Debug mode is ON")

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
    ctx.obj = AppContext(store, debug=debug, dry_run=dry_run)


register_commands()

if __name__ == "__main__":
    cli()
