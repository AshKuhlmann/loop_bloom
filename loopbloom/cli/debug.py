import json
import os
import sqlite3
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
    cfg_path = str(config.get("data_path") or "")
    # Determine path precedence:
    # 1) env (sqlite-specific or generic), 2) config, 3) defaults
    path = (
        os.getenv("LOOPBLOOM_SQLITE_PATH")
        or os.getenv("LOOPBLOOM_DATA_PATH")
        or cfg_path
        or str(JSON_DEFAULT_PATH)
    )
    lower = str(path).lower()
    # Decide backend by file extension when possible, matching the CLI behavior
    if lower.endswith((".db", ".sqlite")):
        storage = "sqlite"
    elif lower.endswith(".json"):
        storage = "json"
    else:
        storage = config.get("storage", "json")

    if storage == "sqlite":
        path = path or str(SQLITE_DEFAULT_PATH)
        db_path = Path(path)
        if not db_path.exists():
            ui.warn("Goals database not found.")
            return
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute("SELECT payload FROM raw_json LIMIT 1")
                row = cur.fetchone()
        except Exception as exc:  # pragma: no cover - rare runtime failures
            ui.error(f"Failed to read SQLite payload: {exc}")
            return
        payload = row[0] if row and row[0] else "[]"
        # Ensure pretty-printed JSON output; fall back to raw payload if parsing fails.
        try:
            console.print_json(payload)
        except Exception:
            console.print_json(json.dumps(json.loads(payload)))
        return
    else:
        path = path or str(JSON_DEFAULT_PATH)
        data_file = Path(path)
        if not data_file.exists():
            ui.warn("Goals file not found.")
            return
        with open(data_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        console.print_json(json.dumps(state))


debug_state_cmd = debug_state
