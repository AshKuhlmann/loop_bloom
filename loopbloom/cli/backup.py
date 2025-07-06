"""Command for saving a timestamped copy of the data file.

The storage backend (JSON or SQLite) is detected at runtime so backups
always mirror the user's active configuration.
"""

from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

import click

from loopbloom.core import config as cfg
from loopbloom.storage.json_store import DEFAULT_PATH as JSON_DEFAULT_PATH
from loopbloom.storage.sqlite_store import DEFAULT_PATH as SQLITE_DEFAULT_PATH

logger = logging.getLogger(__name__)


def _backup_dir() -> Path:
    """Return ``APP_DIR/backups`` ensuring it exists."""
    # ``APP_DIR`` points to the user's configuration directory. We keep
    # backups alongside configuration so they don't clutter the working
    # directory and remain outside of version control by default.
    path = cfg.APP_DIR / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return path


@click.command(name="backup", help="Copy data file to backups directory.")
def backup() -> None:
    """Copy the active data file into :data:`BACKUP_DIR`."""
    config = cfg.load()
    storage = config.get("storage", "json")
    # Allow the user to relocate the data file via configuration. This keeps
    # backups in sync with whatever path they have chosen.
    cfg_path = str(config.get("data_path") or "")

    if storage == "sqlite":
        sqlite_env = os.getenv("LOOPBLOOM_SQLITE_PATH")
        # Environment variable beats config which beats package default
        # so power users can redirect data without editing config.
        path = sqlite_env or cfg_path or str(SQLITE_DEFAULT_PATH)
    else:
        data_env = os.getenv("LOOPBLOOM_DATA_PATH")
        path = data_env or cfg_path or str(JSON_DEFAULT_PATH)

    src = Path(path)
    logger.info("Backing up %s", src)
    if not src.exists():
        logger.error("Data file not found: %s", src)
        click.echo(f"[red]Data file not found: {src}")
        return

    timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    dest = _backup_dir() / f"{src.stem}-backup-{timestamp}{src.suffix}"
    logger.info("Copying to %s", dest)
    try:
        shutil.copy2(src, dest)
        logger.info("Backup saved to %s", dest)
        click.echo(f"[green]Backup saved → {dest}")
    except Exception as exc:
        logger.error("Backup failed: %s", exc)
        click.echo("[red]Backup failed.")


backup_cmd = backup
