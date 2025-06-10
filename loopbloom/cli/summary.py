"""Summary banner with optional per-goal view."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

import click
from rich.console import Console
from rich.table import Table

from loopbloom.cli import with_goals
from loopbloom.core.models import GoalArea

console = Console()

WINDOW = 14  # days


@click.command(
    name="summary",
    help="Show overall or per-goal progress banner.",
)
@click.option(
    "--goal",
    "goal_name",
    default=None,
    help="Show detail for one goal.",
)
@with_goals
def summary(ctx, goal_name: str | None, goals: List[GoalArea]):  # type: ignore
    """Display a progress overview or detail view for a specific goal."""
    if goal_name:
        _detail_view(goal_name, goals)
    else:
        _overview(goals)


def _overview(goals: List[GoalArea]) -> None:
    table = Table(title="LoopBloom Progress (last 14\u00a0days)")
    table.add_column("Goal")
    table.add_column("Successes")
    table.add_column("Next Action")
    today = date.today()

    for g in goals:
        successes = 0
        total = 0
        for ph in g.phases:
            for m in ph.micro_goals:
                for ci in m.checkins:
                    if ci.date >= today - timedelta(days=WINDOW - 1):
                        total += 1
                        if ci.success:
                            successes += 1
        ratio = f"{successes}/{total}" if total else "\u2013"
        table.add_row(g.name, ratio, "Run `--goal` for details")
    console.print(table)


def _detail_view(goal_name: str, goals: List[GoalArea]) -> None:
    g = next((x for x in goals if x.name.lower() == goal_name.lower()), None)
    if not g:
        click.echo("[red]Goal not found.")
        return
    # find active micro
    mg = None
    for ph in g.phases:
        mg = next((m for m in ph.micro_goals if m.status == "active"), None)
        if mg:
            break
    if mg is None:
        click.echo("[yellow]No active micro-goal.")
        return
    successes = sum(ci.success for ci in mg.checkins[-WINDOW:])
    console.print(f"[bold]{g.name} \u2192 {mg.name}[/bold]")
    total = len(mg.checkins[-WINDOW:])
    console.print(f"Success rate last 14\u00a0days: {successes}/{total}")
