"""`loopbloom config` command for viewing or changing settings."""

import json
from typing import Any

import click

from loopbloom.core import config as cfg


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
    click.echo(json.dumps(cfg.load(), indent=2))


@config.command(name="get", help="Get a single key (dot-notation).")
@click.argument("key")
def _get(key: str) -> None:
    """Retrieve a specific key via dot-notation."""
    val: Any = cfg.load()
    # Walk the nested dictionaries using ``.`` as a separator.
    for part in key.split("."):
        val = val.get(part) if isinstance(val, dict) else None
    if val is None:
        click.echo("[red]Key not found.")
        click.echo("Run 'loopbloom config view' to inspect available keys.")
    else:
        click.echo(val)


@config.command(name="set", help="Set a key to a value.")
@click.argument("key")
@click.argument("value")
def _set(key: str, value: str) -> None:
    """Set ``key`` to ``value`` with naive type casting."""
    conf = cfg.load()
    parts = key.split(".")
    d = conf
    # Traverse/construct nested dictionaries until the final segment.
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
    # Assign the converted value and persist.
    d[parts[-1]] = cast
    cfg.save(conf)
    click.echo("[green]Saved.")
