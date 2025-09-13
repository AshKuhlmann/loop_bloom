import json
import os
from pathlib import Path

import click

from loopbloom.cli import ui

from loopbloom.core import config as cfg
from loopbloom.storage.json_store import DEFAULT_PATH as JSON_DEFAULT_PATH
from loopbloom.storage.sqlite_store import DEFAULT_PATH as SQLITE_DEFAULT_PATH

console = ui.console


@click.command(name="debug-state", help="Dump raw JSON goal state.")
def debug_state() -> None:
    """Print the contents of the current goals file."""
    config = cfg.load()
    storage = config.get("storage", "json")
    cfg_path = str(config.get("data_path") or "")
    if storage == "sqlite":
        path = (
            os.getenv("LOOPBLOOM_SQLITE_PATH") or cfg_path or str(SQLITE_DEFAULT_PATH)
        )
    else:
        path = os.getenv("LOOPBLOOM_DATA_PATH") or cfg_path or str(JSON_DEFAULT_PATH)
    data_file = Path(path)
    if not data_file.exists():
        ui.warn("Goals file not found.")
        return
    with open(data_file, "r") as f:
        state = json.load(f)
    console.print_json(json.dumps(state))


debug_state_cmd = debug_state
