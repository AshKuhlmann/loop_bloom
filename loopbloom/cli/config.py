"""`loopbloom config` command for viewing or changing settings."""

import json
from typing import Any

import click

from loopbloom.core import config as cfg


@click.group(name="config", help="View or change LoopBloom settings.")
def config() -> None:
    """Manage configuration settings."""
    pass


@config.command(name="view", help="Print current configuration.")
def _view() -> None:
    """Print the entire configuration as JSON."""
    click.echo(json.dumps(cfg.load(), indent=2))


@config.command(name="get", help="Get a single key (dot-notation).")
@click.argument("key")
def _get(key: str) -> None:
    """Retrieve a specific key via dot-notation."""
    val: Any = cfg.load()
    for part in key.split("."):
        val = val.get(part) if isinstance(val, dict) else None
    if val is None:
        click.echo("[red]Key not found.")
    else:
        click.echo(val)


@config.command(name="set", help="Set a key to a value.")
@click.argument("key")
@click.argument("value")
def _set(key: str, value: str) -> None:
    """Set KEY to VALUE with naive type casting."""
    conf = cfg.load()
    parts = key.split(".")
    d = conf
    for p in parts[:-1]:
        d = d.setdefault(p, {})
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
    d[parts[-1]] = cast
    cfg.save(conf)
    click.echo("[green]Saved.")
