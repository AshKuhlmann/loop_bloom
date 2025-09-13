"""Display a progress summary banner.

When called without ``--goal`` a table showing recent success ratios is
printed. Passing ``--goal`` focuses the output on a single micro-habit and
checks whether it should be advanced.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import List

import click
from rich.console import Group
from rich.progress_bar import ProgressBar
from rich.table import Table

from loopbloom.cli import with_goals
from loopbloom.cli import ui
from loopbloom.cli.utils import goal_not_found
from loopbloom.constants import WINDOW_DEFAULT
from loopbloom.core import config as cfg
from loopbloom.core.models import GoalArea
from loopbloom.core.progression import should_advance
from loopbloom.services.datetime import get_current_datetime

console = ui.console

logger = logging.getLogger(__name__)


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
    # Show a compact summary row for each goal. Successes are calculated using
    # the configured window so the overview matches the user's advancement
    # settings.
    window = cfg.load().get("advance", {}).get("window", WINDOW_DEFAULT)
    table = Table(title=f"LoopBloom Progress (last {window}\u00a0days)")
    table.add_column("Goal")
    table.add_column("Successes")
    table.add_column("Next Action")
    today = get_current_datetime().date()

    for g in goals:
        successes = 0
        total = 0
        # Collect check-ins from every micro-habit so the goal's progress
        # reflects all activity beneath it.
        all_checkins = []
        # Grab check-ins from phases first
        for ph in g.phases:
            for m in ph.micro_goals:
                all_checkins.extend(m.checkins)
        # Then include micro-goals attached directly to the goal
        for m in g.micro_goals:
            all_checkins.extend(m.checkins)

        for ci in all_checkins:
            if ci.date >= today - timedelta(days=window - 1):
                total += 1
                if ci.success:
                    successes += 1
        ratio: Group | str
        if total:
            # Display a progress bar to make the ratio easier to scan at a
            # glance.
            bar = ProgressBar(total=total, completed=successes)
            ratio = Group(bar, f" {successes}/{total}")
        else:
            ratio = "\u2013"

        # Determine which micro-habit is currently active so we can suggest
        # whether the goal should advance.
        active = g.get_active_micro_goal()
        flag = "Advance?" if active and should_advance(active) else "\u2014"
        table.add_row(g.name, ratio, flag)
    console.print(table)


def _detail_view(goal_name: str, goals: List[GoalArea]) -> None:
    # Show focused statistics for a single goal using the same window length
    # as the advancement logic so the recommendations are consistent.
    window = cfg.load().get("advance", {}).get("window", WINDOW_DEFAULT)
    # Look up the requested goal so we can inspect its check-ins.
    g = next((x for x in goals if x.name.lower() == goal_name.lower()), None)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])
        return
    # Identify which micro-habit is currently active to evaluate its progress
    # in isolation.
    mg = g.get_active_micro_goal()

    if mg is None:
        logger.info("No active micro-goal for %s", goal_name)
        ui.warn("No active micro-goal.")
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
    # If the micro-habit meets the advancement criteria send a reminder via the
    # user's preferred notification channel.
    from loopbloom.services import notifier

    if should_advance(mg):
        notifier.send(
            "LoopBloom",
            f"Consider advancing '{mg.name}'",
            mode=cfg.load().get("notify", "terminal"),
            goal=g.name,
        )


summary_cmd = summary
