"""Export goal history to CSV or JSON.

The exported format is intentionally simple so the data can be analysed in
spreadsheets or external tools without knowing the internal model
structure.
"""

import csv
import json
import logging
from typing import List

import click

from loopbloom.storage.base import Storage

logger = logging.getLogger(__name__)


@click.command(name="export", help="Export data to CSV or JSON.")
@click.option(
    "--fmt",
    type=click.Choice(["csv", "json"]),
    required=True,
    help="Output format (csv or json).",
)
@click.option(
    "--out",
    "out_path",
    type=click.Path(),
    required=True,
    help="File to write exported data to.",
)
@click.pass_obj
def export(store: Storage, fmt: str, out_path: str) -> None:
    """Write all goal history to OUT_PATH in format FMT.

    Usage: ``loopbloom export --fmt csv --out progress.csv``
    """
    # Use whichever storage backend the user configured so exports always match
    # their real data.
    logger.info("Exporting data to %s as %s", out_path, fmt)
    goals = store.load()

    if fmt == "json":
        with open(out_path, "w", encoding="utf-8") as fp:
            json.dump([g.model_dump(mode="json") for g in goals], fp, indent=2)
        logger.info("JSON export complete")
        click.echo(f"[green]Exported JSON → {out_path}")
        return

    # CSV output is a flat table – one row per check-in – to make importing the
    # data into spreadsheets straightforward. The first row acts as the header.
    rows: List[List[str]] = [
        [
            "date",
            "goal",
            "phase",
            "micro",
            "success",
            "note",
        ]
    ]
    for g in goals:
        for ph in g.phases:
            for m in ph.micro_goals:
                for ci in m.checkins:
                    # Collapse the hierarchical objects into a row so external
                    # tools don't need to understand our data model.
                    rows.append(
                        [
                            str(ci.date),
                            g.name,
                            ph.name,
                            m.name,
                            "1" if ci.success else "0",
                            (ci.note or "").replace("\n", " "),
                        ]
                    )
    with open(out_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerows(rows)
    logger.info("CSV export complete")
    click.echo(f"[green]Exported CSV → {out_path}")


export_cmd = export
