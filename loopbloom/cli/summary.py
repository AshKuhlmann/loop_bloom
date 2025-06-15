"""Summary banner with optional per-goal view."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List

import click
from rich.console import Console, Group
from rich.table import Table
from rich.progress_bar import ProgressBar

from loopbloom.cli import with_goals
from loopbloom.cli.utils import goal_not_found
from loopbloom.core import config as cfg
from loopbloom.core.models import GoalArea
from loopbloom.core.progression import should_advance

console = Console()

WINDOW_DEFAULT = 14  # days


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
def summary(goal_name: str | None, goals: List[GoalArea]):  # type: ignore
    """Display a progress overview or detail view for a specific goal."""
    if goal_name:
        _detail_view(goal_name, goals)
    else:
        _overview(goals)


def _overview(goals: List[GoalArea]) -> None:
    window = cfg.load().get("advance", {}).get("window", WINDOW_DEFAULT)
    table = Table(title=f"LoopBloom Progress (last {window}\u00a0days)")
    table.add_column("Goal")
    table.add_column("Successes")
    table.add_column("Next Action")
    today = date.today()

    for g in goals:
        successes = 0
        total = 0
        all_checkins = []
        # Aggregate checkins from phases
        for ph in g.phases:
            for m in ph.micro_goals:
                all_checkins.extend(m.checkins)
        # Aggregate checkins from direct micro-goals
        for m in g.micro_goals:
            all_checkins.extend(m.checkins)

        for ci in all_checkins:
            if ci.date >= today - timedelta(days=window - 1):
                total += 1
                if ci.success:
                    successes += 1
        ratio: Group | str
        if total:
            bar = ProgressBar(total=total, completed=successes)
            ratio = Group(bar, f" {successes}/{total}")
        else:
            ratio = "\u2013"

        # Find the active micro-goal
        active = g.get_active_micro_goal()
        flag = "Advance?" if active and should_advance(active) else "\u2014"
        table.add_row(g.name, ratio, flag)
    console.print(table)


def _detail_view(goal_name: str, goals: List[GoalArea]) -> None:
    window = cfg.load().get("advance", {}).get("window", WINDOW_DEFAULT)
    g = next((x for x in goals if x.name.lower() == goal_name.lower()), None)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])
        return
    # Update logic to find the active micro-goal
    mg = g.get_active_micro_goal()

    if mg is None:
        click.echo("[yellow]No active micro-goal.")
        return
    successes = sum(ci.success for ci in mg.checkins[-window:])
    suggest = should_advance(mg)
    flag = "[green]Advance? (≥ 80 %)" if suggest else "✦"
    console.print(f"[bold]{g.name} \u2192 {mg.name}[/bold]")
    total = len(mg.checkins[-window:])
    progress: Group | str
    if total:
        bar = ProgressBar(total=total, completed=successes)
        progress = Group(bar, f" {successes}/{total}")
    else:
        progress = "\u2013"
    console.print(
        f"Success rate last {window}\u00a0days: ",
        progress,
        f"  {flag}",
    )
    # notify if eligible for advancement
    from loopbloom.services import notifier

    if should_advance(mg):
        notifier.send(
            "LoopBloom",
            f"Consider advancing '{mg.name}'",
            mode=cfg.load().get("notify", "terminal"),
        )
