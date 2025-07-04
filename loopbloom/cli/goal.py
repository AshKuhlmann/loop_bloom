"""LoopBloom CLI: goal, phase, and micro-habit CRUD."""

import logging
from typing import List, Optional

import click

from loopbloom.cli import with_goals
from loopbloom.cli.interactive import choose_from
from loopbloom.cli.utils import (
    find_goal,
    find_phase,
    get_goal_from_name,
    goal_not_found,
    save_goal,
)
from loopbloom.core.models import GoalArea, MicroGoal, Phase

logger = logging.getLogger(__name__)


@click.group(name="goal", help="Manage goals, phases, and micro-habits.")
def goal() -> None:
    """Goal-level commands."""
    # Acts solely as a container for subcommands like ``goal add`` and
    # ``goal rm``.
    pass


@goal.command(name="add")
@click.argument("name")
@click.option("--notes", default="", help="Optional notes for this goal.")
@with_goals
def goal_add(name: str, notes: str, goals: List[GoalArea]) -> None:
    """Add a new goal area."""
    if find_goal(goals, name):
        logger.error("Goal already exists: %s", name)
        click.echo("[yellow]Goal already exists.")
        return
    goals.append(GoalArea(name=name.strip(), notes=notes or None))
    logger.info("Added goal %s", name)
    click.echo(f"[green]Added goal:[/] {name}")


@goal.command(name="list")
@with_goals
def goal_list(goals: List[GoalArea]) -> None:
    """List all goal areas."""
    if not goals:
        logger.info("No goals to list")
        click.echo("[italic]No goals – use `loopbloom goal add`.")
        return
    for g in goals:
        note = f" - {g.notes}" if g.notes else ""
        click.echo(f"• {g.name} (phases: {len(g.phases)}){note}")


@goal.command(name="rm")
@click.argument("name", required=False)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
@with_goals
def goal_rm(
    name: Optional[str],
    yes: bool,
    goals: List[GoalArea],
) -> None:
    """Remove a goal area.

    If ``name`` is omitted, the command interactively asks which goal to
    delete.
    """
    # Prompt interactively when no goal name is provided.
    if name is None:
        if not goals:
            logger.info("No goals to remove")
            msg = "[italic]No goals – nothing to remove."
            click.echo(msg)  # pragma: no cover
            return  # pragma: no cover
        click.echo("Which goal do you want to delete?")  # pragma: no cover
        selected = choose_from(
            [g.name for g in goals],
            "Enter number",
        )  # pragma: no cover
        if selected is None:
            return  # pragma: no cover
        name = selected

    g = find_goal(goals, name)
    if not g:
        logger.error("Goal not found for deletion: %s", name)
        goal_not_found(name, [g.name for g in goals])
        return
    # Confirm destructive operation unless --yes was supplied.
    if not yes and not click.confirm(
        f"Delete goal '{name}'?",
        default=False,
    ):
        return
    goals.remove(g)
    logger.info("Deleted goal %s", name)
    click.echo(f"[green]Deleted goal:[/] {name}")


@goal.command(name="notes", help="View and edit goal notes in $EDITOR.")
@click.argument("name")
@click.pass_context
def goal_notes(ctx: click.Context, name: str) -> None:
    """Open ``name``'s notes in the user's editor."""
    goal = get_goal_from_name(name)
    if not goal:
        goal_not_found(name, [])
        raise click.Abort()

    edited = click.edit(goal.notes or "")
    if edited is None:
        click.echo(goal.notes or "")
    else:
        goal.notes = edited.strip()
        save_goal(goal)
        click.echo(f"[green]Notes for goal '{name}' updated.")


# Phase commands
@goal.group(name="phase", help="Phase-level commands.")
def phase() -> None:
    """Phase-level subcommands."""
    # Like :func:`goal`, this group merely groups related actions and does not
    # run any code itself.
    pass


@phase.command(name="add")
@click.argument("goal_name", required=False)
@click.argument("phase_name")
@click.option("--notes", default="", help="Optional notes for the phase.")
@with_goals
def phase_add(
    goal_name: Optional[str],
    phase_name: str,
    notes: str,
    goals: List[GoalArea],
) -> None:
    """Add a new phase under a goal.

    If ``goal_name`` is omitted, the command interactively prompts you to
    select the goal.
    """
    # Prompt for the goal when not provided on the command line.
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            logger.error("No goals for phase addition")
            msg = "[red]No goals – use `loopbloom goal add`."
            click.echo(msg)  # pragma: no cover
            return  # pragma: no cover
        click.echo("Select goal for new phase:")  # pragma: no cover
        goal_name = choose_from(
            names,
            "Enter number",
        )  # pragma: no cover
        if goal_name is None:
            return  # pragma: no cover

    g = find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover
    # Avoid duplicates when the phase already exists.
    if find_phase(g, phase_name):
        logger.error("Phase already exists: %s/%s", goal_name, phase_name)
        click.echo("[yellow]Phase exists.")
        return
    g.phases.append(Phase(name=phase_name.strip(), notes=notes or None))
    logger.info("Added phase %s under %s", phase_name, goal_name)
    click.echo(f"[green]Added phase '{phase_name}' to {goal_name}")


@phase.command(name="rm")
@click.argument("goal_name", required=False)
@click.argument("phase_name", required=False)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
@with_goals
def phase_rm(
    goal_name: Optional[str],
    phase_name: Optional[str],
    yes: bool,
    goals: List[GoalArea],
) -> None:
    """Remove a phase from a goal.

    If ``goal_name`` or ``phase_name`` is omitted, the command
    interactively asks you to choose the missing value.
    """
    # Ask which goal to operate on if not provided.
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            logger.error("No goals for phase removal")
            msg = "[red]No goals – use `loopbloom goal add`."
            click.echo(msg)  # pragma: no cover
            return  # pragma: no cover
        click.echo("Select goal:")  # pragma: no cover
        goal_name = choose_from(
            names,
            "Enter number",
        )  # pragma: no cover
        if goal_name is None:
            return  # pragma: no cover

    g = find_goal(goals, goal_name)
    if not g:
        logger.error("Goal not found for phase removal: %s", goal_name)
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover

    # When no phase is specified, offer a menu of existing ones.
    if phase_name is None:
        options = [p.name for p in g.phases]
        if not options:
            logger.error("No phases in goal %s", goal_name)
            msg = "[red]No phases found for this goal."
            click.echo(msg)  # pragma: no cover
            return  # pragma: no cover
        click.echo("Select phase to delete:")  # pragma: no cover
        phase_name = choose_from(
            options,
            "Enter number",
        )  # pragma: no cover
        if phase_name is None:
            return  # pragma: no cover

    # Locate the phase object for deletion.
    p = find_phase(g, phase_name)
    if not p:
        logger.error("Phase not found: %s/%s", goal_name, phase_name)
        click.echo("[red]Phase not found.")  # pragma: no cover
        return  # pragma: no cover

    if not yes and not click.confirm(
        f"Delete phase '{phase_name}' from {goal_name}?",
        default=False,
    ):
        return
    g.phases.remove(p)
    logger.info("Deleted phase %s from %s", phase_name, goal_name)
    click.echo(f"[green]Deleted phase '{phase_name}' from {goal_name}")


@phase.command(
    name="notes",
    help="View and edit notes for a phase in $EDITOR.",
)
@click.argument("goal_name")
@click.argument("phase_name")
@click.pass_context
def phase_notes(ctx: click.Context, goal_name: str, phase_name: str) -> None:
    """Open notes for ``phase_name`` under ``goal_name`` in the editor."""
    goal = get_goal_from_name(goal_name)
    if not goal:
        goal_not_found(goal_name, [])
        raise click.Abort()
    phase = find_phase(goal, phase_name)
    if not phase:
        click.echo("[red]Phase not found.")
        raise click.Abort()

    edited = click.edit(phase.notes or "")
    if edited is None:
        click.echo(phase.notes or "")
    else:
        phase.notes = edited.strip()
        save_goal(goal)
        msg = "[green]Notes for phase '{}' under {} updated.".format(
            phase_name,
            goal_name,
        )
        click.echo(msg)


@goal.command(
    name="wizard",
    help="Interactive wizard to create goal, phase, and micro-habit.",
)
@with_goals
def goal_wizard(goals: List[GoalArea]) -> None:
    """Guide user through creating a full goal hierarchy."""
    logger.info("Starting goal wizard")
    click.echo("Let's set up your first goal!")
    goal_name = click.prompt("Goal name").strip()
    if find_goal(goals, goal_name):
        logger.error("Goal already exists during wizard: %s", goal_name)
        click.echo("[red]Goal already exists.")
        return
    phase_name = click.prompt("First phase name").strip()
    micro_name = click.prompt("First micro-habit name").strip()

    new_goal = GoalArea(name=goal_name)
    new_phase = Phase(name=phase_name)
    new_phase.micro_goals.append(MicroGoal(name=micro_name))
    new_goal.phases.append(new_phase)
    goals.append(new_goal)
    logger.info(
        "Created goal %s with phase %s and micro %s",
        goal_name,
        phase_name,
        micro_name,
    )

    msg = (
        f"[green]Created goal '{goal_name}' "
        f"with phase '{phase_name}' and micro '{micro_name}'."
    )
    click.echo(msg)
