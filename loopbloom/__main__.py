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
from loopbloom.cli import ui
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


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--debug", is_flag=True, help="Enable debug mode with verbose logging.")
@click.option(
    "--dry-run", is_flag=True, help="Simulate commands without saving changes."
)
@click.option(
    "--no-color",
    "--plain",
    "no_color",
    is_flag=True,
    help="Disable colored/styled output.",
)
@click.option(
    "--data-path",
    "data_path_opt",
    default=None,
    help="Override data file path for this session.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    debug: bool,
    dry_run: bool,
    no_color: bool,
    data_path_opt: str | None,
) -> None:
    """LoopBloom – tiny habits, big momentum."""
    # Configure UI before commands print anything.
    ui.configure(no_color=no_color)
    register_commands()
    setup_logging(level=logging.DEBUG if debug else logging.INFO)
    if debug:
        logging.getLogger().debug("Debug mode is ON")
        click.echo("Debug mode is ON")

    config = cfg.load()
    storage_backend = os.getenv("LOOPBLOOM_STORAGE_BACKEND", config.get("storage", "json"))
    # Precedence: CLI flag > env var > config
    data_path = data_path_opt or os.getenv("LOOPBLOOM_DATA_PATH", config.get("data_path"))

    # If an explicit data path is provided, prefer a backend based on
    # the file extension to avoid mismatches (e.g., tests may set
    # LOOPBLOOM_DATA_PATH to a JSON file regardless of user config).
    if data_path:
        lower = str(data_path).lower()
        if lower.endswith(".json"):
            storage_backend = "json"
        elif lower.endswith(".db") or lower.endswith(".sqlite"):
            storage_backend = "sqlite"

    store: Storage
    if storage_backend == "sqlite":
        path = data_path or str(SQLITE_DEFAULT_PATH)
        store = SQLiteStore(path)
    else:
        path = data_path or str(JSON_DEFAULT_PATH)
        store = JSONStore(path)

    # Expose the store instance to subcommands via Click's context object.
    ctx.obj = AppContext(store, debug=debug, dry_run=dry_run)


register_commands()

if __name__ == "__main__":
    cli()
