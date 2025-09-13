"""`loopbloom config` command for viewing or changing settings.

This module exposes a small configuration editor for the CLI. Settings are
stored in a user-specific TOML file and control things like the storage backend
and notification style.
"""

import json
import logging
from pathlib import Path
from typing import Any, cast

import click

from loopbloom.cli import ui
from loopbloom.core import config as cfg
from loopbloom.storage.base import Storage

logger = logging.getLogger(__name__)


@click.group(name="config", help="View or change LoopBloom settings.")
def config() -> None:
    """Manage configuration settings."""
    # This group exposes subcommands like ``get`` and ``set`` for manipulating
    # the ``config.toml`` file. Without subcommands Click would execute this
    # function directly, so we leave the body empty.
    pass


@config.command(name="view", help="Print current configuration.")
def _view() -> None:
    """Print the entire configuration as JSON."""
    # ``json.dumps`` makes the output easier to pipe into other tools.
    logger.info("Viewing config")
    click.echo(json.dumps(cfg.load(), indent=2))


@config.command(name="get", help="Get a single key (dot-notation).")
@click.argument("key")
def _get(key: str) -> None:
    """Retrieve a specific configuration value.

    Args:
        key: Dot-separated key, e.g. ``advance.window``.
    """
    # ``key`` may contain dots to access nested sections, e.g. ``advance.window``
    # refers to ``{"advance": {"window": ...}}`` inside the TOML file.
    val: Any = cfg.load()
    # Traverse the nested dictionaries using ``.`` so arbitrarily deep keys can
    # be read.
    for part in key.split("."):
        val = val.get(part) if isinstance(val, dict) else None
    if val is None:
        logger.error("Config key not found: %s", key)
        ui.error("Key not found.")
        ui.info("Run 'loopbloom config view' to inspect available keys.")
    else:
        logger.info("Config get %s -> %s", key, val)
        click.echo(val)


@config.command(name="set", help="Set a key to a value.")
@click.argument("key")
@click.argument("value")
def _set(key: str, value: str) -> None:
    """Set ``key`` to ``value`` with naive type casting.

    Args:
        key: Dot-separated key to update.
        value: New value as string; basic types are coerced automatically.
    """
    conf = cfg.load()
    parts = key.split(".")
    d = conf
    # Create parent sections on the fly so ``config set a.b.c`` works even when
    # ``a`` or ``b`` don't exist yet.
    for p in parts[:-1]:
        d = d.setdefault(p, {})
    # Convert the string to int/float/bool when possible so numbers are not
    # stored as strings in the config file.
    if value.isdigit():
        cast: Any = int(value)
    else:
        try:
            cast = float(value)
        except ValueError:
            lower = value.lower()
            if lower in ("true", "false"):
                cast = lower == "true"
            else:
                cast = value
    if key == "advance.strategy":
        lower = str(cast).lower()
        if lower not in ("ratio", "streak"):
            ui.error("Invalid strategy. Use 'ratio' or 'streak'.")
            return
        cast = lower
    # Assign the converted value and persist.
    d[parts[-1]] = cast
    cfg.save(conf)
    logger.info("Config set %s", key)
    ui.success("Saved.")


@config.command(name="reset", help="Reset all user data and goals.")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
@click.pass_context
def reset(ctx: click.Context, yes: bool) -> None:
    """Reset all user data and goals."""
    if not yes and not click.confirm(
        "This will delete all your LoopBloom data and goals. Are you sure?",
        default=False,
    ):
        ui.warn("Reset cancelled.")
        return

    store: Storage = ctx.obj.store
    # ``_path`` is a private attribute on concrete stores; cast to ``Any``
    # for mypy since it's not part of the ``Storage`` protocol.
    data_path = Path(cast(Any, store)._path)

    try:
        if data_path.exists():
            if data_path.is_file():
                data_path.unlink()  # Delete the file
            elif data_path.is_dir():
                # If it's a directory (e.g., for SQLite with multiple files),
                # remove recursively.
                import shutil

                shutil.rmtree(data_path)
            ui.success(f"Successfully deleted data at: {data_path}")
        else:
            ui.warn("No data found to reset.")
    except Exception as e:
        ui.error(f"Error resetting data: {e}")
        logger.error(f"Error resetting data: {e}")


config_cmd = config
