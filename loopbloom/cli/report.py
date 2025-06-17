"""Advanced reports for LoopBloom."""

from __future__ import annotations

from calendar import Calendar, month_name
from datetime import date
from typing import Iterable, Iterator, List

import click
from rich.console import Console, Group, RenderableType
from rich.progress_bar import ProgressBar
from rich.table import Table

from loopbloom.cli import with_goals
from loopbloom.core.models import GoalArea, MicroGoal

console = Console()


@click.command(
    name="report",
    help="Show calendar heatmap or success bars for goals.",
)
@click.option(
    "--mode",
    type=click.Choice(["calendar", "success"], case_sensitive=False),
    default="calendar",
    help="Report type to display.",
)
@with_goals
def report(mode: str, goals: List[GoalArea]) -> None:
    """Display advanced reports based on ``mode``."""
    if mode == "success":
        _success_bars(goals)
    else:
        _calendar_heatmap(goals)


def _gather_all_micro(goals: Iterable[GoalArea]) -> Iterator[MicroGoal]:
    """Yield all micro-goals from ``goals``."""
    for g in goals:
        for ph in g.phases:
            for m in ph.micro_goals:
                yield m
        for m in g.micro_goals:
            yield m


def _calendar_heatmap(goals: List[GoalArea]) -> None:
    """Print an ASCII calendar heatmap of the current month."""
    today = date.today()
    cal = Calendar()
    # Build map of day -> (successes, total)
    stats: dict[int, tuple[int, int]] = {}
    for m in _gather_all_micro(goals):
        for ci in m.checkins:
            if ci.date.year == today.year and ci.date.month == today.month:
                succ, tot = stats.get(ci.date.day, (0, 0))
                if ci.success:
                    succ += 1
                tot += 1
                stats[ci.date.day] = (succ, tot)

    weeks = cal.monthdayscalendar(today.year, today.month)
    title = (
        "LoopBloom Check-in Heatmap – "
        f"{month_name[today.month]} {today.year}"
    )
    console.print(f"[bold]{title}[/bold]")
    for week in weeks:
        line = ""
        for day in week:
            if day == 0:
                line += "   "
                continue
            succ, tot = stats.get(day, (0, 0))
            char = "·"  # dot
            if tot:
                char = "░"  # light shade for skips
                if succ:
                    char = "▓"  # dark shade
            line += f"{char} "
        console.print(line.rstrip())


def _success_bars(goals: List[GoalArea]) -> None:
    """Show a bar chart of success rates per goal."""
    table = Table(title="Success Rates per Goal")
    table.add_column("Goal")
    table.add_column("Rate")
    for g in goals:
        successes = 0
        total = 0
        for m in _gather_all_micro([g]):
            for ci in m.checkins:
                total += 1
                if ci.success:
                    successes += 1
        ratio: RenderableType
        if total:
            bar = ProgressBar(total=total, completed=successes, width=20)
            ratio = Group(bar, f" {successes}/{total}")
        else:
            ratio = "–"
        table.add_row(g.name, ratio)
    console.print(table)
