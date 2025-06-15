"""CLI commands for micro-habit lifecycle management."""

from typing import List, Optional

import click

from loopbloom.cli import with_goals
from loopbloom.cli.utils import goal_not_found
from loopbloom.core.models import GoalArea, MicroGoal, Phase, Status


def _find_goal(goals: List[GoalArea], name: str) -> Optional[GoalArea]:
    """Return matching goal if present."""
    return next((g for g in goals if g.name.lower() == name.lower()), None)


def _find_phase(goal: GoalArea, name: str) -> Optional[Phase]:
    """Return phase from ``goal`` matching ``name`` if found."""
    return next(
        (p for p in goal.phases if p.name.lower() == name.lower()),
        None,
    )


@click.group(name="micro", help="Micro-habit operations.")
def micro() -> None:
    """Top-level micro-habit commands."""
    pass


@micro.command(name="complete")
@click.argument("name")
@click.option(
    "--goal",
    "goal_name",
    required=True,
    help="Goal containing this micro-habit.",
)
@click.option(
    "--phase",
    "phase_name",
    default=None,
    help="Phase containing this micro-habit.",
)
@with_goals
def micro_complete(
    name: str,
    goal_name: str,
    phase_name: Optional[str],
    goals: List[GoalArea],
) -> None:
    """Mark a micro-habit as complete."""
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])
        return

    target_list: List[MicroGoal]
    if phase_name:
        p = _find_phase(g, phase_name)
        if not p:
            click.echo(f"[red]Phase '{phase_name}' not found.")
            return
        target_list = p.micro_goals
    else:
        target_list = g.micro_goals

    mg = next((m for m in target_list if m.name.lower() == name.lower()), None)
    if not mg:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return

    mg.status = Status.complete
    click.echo(f"[green]Marked micro-habit '{name}' as complete.")


@micro.command(name="cancel")
@click.argument("name")
@click.option(
    "--goal",
    "goal_name",
    required=True,
    help="Goal containing this micro-habit.",
)
@click.option(
    "--phase",
    "phase_name",
    default=None,
    help="Phase containing this micro-habit.",
)
@with_goals
def micro_cancel(
    name: str,
    goal_name: str,
    phase_name: Optional[str],
    goals: List[GoalArea],
) -> None:
    """Cancel a micro-habit without deleting it."""
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])
        return

    target_list: List[MicroGoal]
    if phase_name:
        p = _find_phase(g, phase_name)
        if not p:
            click.echo(f"[red]Phase '{phase_name}' not found.")
            return
        target_list = p.micro_goals
    else:
        target_list = g.micro_goals

    mg = next((m for m in target_list if m.name.lower() == name.lower()), None)
    if not mg:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return

    mg.status = Status.cancelled
    click.echo(f"[green]Cancelled micro-habit '{name}'.")
