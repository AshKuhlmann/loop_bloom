"""CLI commands for micro-habit lifecycle management."""

from typing import List, Optional

import click

from loopbloom.cli import with_goals
from loopbloom.cli.interactive import choose_from
from loopbloom.cli.utils import goal_not_found
from loopbloom.core.models import GoalArea, MicroGoal, Phase, Status


def _find_goal(goals: List[GoalArea], name: str) -> Optional[GoalArea]:
    """Return the goal with ``name`` if present (case-insensitive)."""
    # ``GoalArea`` objects are stored in a simple list so we do a linear
    # search. The number of goals is expected to be small.
    return next((g for g in goals if g.name.lower() == name.lower()), None)


def _find_phase(goal: GoalArea, name: str) -> Optional[Phase]:
    """Return phase from ``goal`` matching ``name`` if found."""
    # Phases are also stored sequentially on the goal.
    return next(
        (p for p in goal.phases if p.name.lower() == name.lower()),
        None,
    )


@click.group(name="micro", help="Micro-habit operations.")
def micro() -> None:
    """Top-level micro-habit commands."""
    # This group owns actions like ``add`` and ``complete``. It doesn't run
    # any logic on its own but organizes related subcommands.
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
    # Locate the parent goal first.
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])
        return

    target_list: List[MicroGoal]
    if phase_name:
        # When a phase is provided we search within it.
        p = _find_phase(g, phase_name)
        if not p:
            click.echo(f"[red]Phase '{phase_name}' not found.")
            return
        target_list = p.micro_goals
    else:
        # Otherwise search micro-goals attached directly to the goal.
        target_list = g.micro_goals

    # Case-insensitive match on micro-habit name.
    mg = next((m for m in target_list if m.name.lower() == name.lower()), None)
    if not mg:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return

    # Persist the new lifecycle state.
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
    # Locate the goal that owns this micro-habit.
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])
        return

    target_list: List[MicroGoal]
    if phase_name:
        # Search within the specified phase when provided.
        p = _find_phase(g, phase_name)
        if not p:
            click.echo(f"[red]Phase '{phase_name}' not found.")
            return
        target_list = p.micro_goals
    else:
        # Otherwise operate on direct micro-goals of the goal.
        target_list = g.micro_goals

    mg = next((m for m in target_list if m.name.lower() == name.lower()), None)
    if not mg:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return

    # Mark the habit as cancelled without deleting history.
    mg.status = Status.cancelled
    click.echo(f"[green]Cancelled micro-habit '{name}'.")


@micro.command(name="add")
@click.argument("name")
@click.option(
    "--goal",
    "goal_name",
    required=False,
    default=None,
    help="The goal to add this to.",
)
@click.option(
    "--phase",
    "phase_name",
    default=None,
    help="Add to a specific phase (created if needed).",
)
@with_goals
def micro_add(
    name: str,
    goal_name: Optional[str],
    phase_name: Optional[str],
    goals: List[GoalArea],
) -> None:
    """Add a new micro-habit to a goal or phase.

    If ``goal_name`` is omitted, the user is prompted to select one.
    If ``phase_name`` is provided but doesn't exist, a new phase will be
    created automatically.
    """
    # If no goal specified, prompt interactively for one.
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            click.echo("[red]No goals – use `loopbloom goal add`.")
            return
        click.echo("Select goal for new micro-habit:")
        goal_name = choose_from(names, "Enter number")
        if goal_name is None:
            return

    # Ensure the referenced goal exists.
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover

    if phase_name is None:
        # Attach the new micro-habit directly to the goal.
        g.micro_goals.append(MicroGoal(name=name.strip()))
        click.echo(f"[green]Added micro-habit '{name}' to goal '{goal_name}'")
        return

    # Phase provided: create or locate the phase first. This lets users add
    # micro-habits to a new phase in a single command.
    p = _find_phase(g, phase_name)
    if not p:
        p = Phase(name=phase_name.strip())
        g.phases.append(p)
        msg = f"[yellow]Created phase '{phase_name}' under goal '{goal_name}'."
        click.echo(msg)
    # Finally add the micro-habit under that phase.
    p.micro_goals.append(MicroGoal(name=name.strip()))
    msg = f"[green]Added micro-habit '{name}' to {goal_name}/{phase_name}"
    click.echo(msg)


@micro.command(name="rm")
@click.argument("name")
@click.option(
    "--goal",
    "goal_name",
    required=True,
    help="The goal to remove from.",
)
@click.option(
    "--phase",
    "phase_name",
    default=None,
    help="Remove from a specific phase.",
)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
@with_goals
def micro_rm(
    name: str,
    goal_name: str,
    phase_name: Optional[str],
    yes: bool,
    goals: List[GoalArea],
) -> None:
    """Remove a micro-habit by its name."""
    # Validate and locate the target goal.
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover

    target_list: Optional[List[MicroGoal]] = None
    if phase_name:
        # Narrow search to a specific phase when supplied.
        p = _find_phase(g, phase_name)
        if not p:
            click.echo(f"[red]Phase '{phase_name}' not found.")
            return
        target_list = p.micro_goals
    else:
        # Otherwise look among the goal's direct micro-habits.
        target_list = g.micro_goals

    mg = next((m for m in target_list if m.name.lower() == name.lower()), None)
    if not mg:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return

    if not yes and not click.confirm(
        f"Permanently delete '{name}'?",
        default=False,
    ):
        return

    target_list.remove(mg)
    click.echo(f"[green]Deleted micro-habit:[/] {name}")
