"""Backup current data file to ``APP_DIR/backups``."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

import click

from loopbloom.core import config as cfg
from loopbloom.storage.json_store import DEFAULT_PATH as JSON_DEFAULT_PATH
from loopbloom.storage.sqlite_store import DEFAULT_PATH as SQLITE_DEFAULT_PATH


def _backup_dir() -> Path:
    """Return ``APP_DIR/backups`` ensuring it exists."""
    path = cfg.APP_DIR / "backups"
    path.mkdir(parents=True, exist_ok=True)
    return path


@click.command(name="backup", help="Copy data file to backups directory.")
def backup() -> None:
    """Copy the active data file into :data:`BACKUP_DIR`."""
    config = cfg.load()
    storage = config.get("storage", "json")
    cfg_path = str(config.get("data_path") or "")

    if storage == "sqlite":
        path = (
            os.getenv("LOOPBLOOM_SQLITE_PATH") or cfg_path or str(SQLITE_DEFAULT_PATH)
        )
    else:
        path = os.getenv("LOOPBLOOM_DATA_PATH") or cfg_path or str(JSON_DEFAULT_PATH)

    src = Path(path)
    if not src.exists():
        click.echo(f"[red]Data file not found: {src}")
        return

    timestamp = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    dest = _backup_dir() / f"{src.stem}-backup-{timestamp}{src.suffix}"
    shutil.copy2(src, dest)
    click.echo(f"[green]Backup saved → {dest}")
