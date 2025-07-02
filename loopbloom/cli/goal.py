"""LoopBloom CLI: goal, phase, and micro-habit CRUD."""

from typing import List, Optional

import click

from loopbloom.cli import with_goals
from loopbloom.cli.utils import goal_not_found
from loopbloom.cli.interactive import choose_from
from loopbloom.core.models import GoalArea, Phase


def _find_goal(goals: List[GoalArea], name: str) -> Optional[GoalArea]:
    """Return the goal matching ``name`` if present (case-insensitive)."""
    return next((g for g in goals if g.name.lower() == name.lower()), None)


def _find_phase(goal: GoalArea, name: str) -> Optional[Phase]:
    """Return the phase within ``goal`` whose name matches ``name``."""
    return next(
        (p for p in goal.phases if p.name.lower() == name.lower()),
        None,
    )


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
    if _find_goal(goals, name):
        click.echo("[yellow]Goal already exists.")
        return
    goals.append(GoalArea(name=name.strip(), notes=notes or None))
    click.echo(f"[green]Added goal:[/] {name}")


@goal.command(name="list")
@with_goals
def goal_list(goals: List[GoalArea]) -> None:
    """List all goal areas."""
    if not goals:
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
    """Remove a goal area. Use ``--yes`` to skip the confirmation prompt."""
    # Prompt interactively when no goal name is provided.
    if name is None:
        if not goals:
            click.echo(
                "[italic]No goals – nothing to remove."
            )  # pragma: no cover
            return  # pragma: no cover
        click.echo(
            "Which goal do you want to delete?"
        )  # pragma: no cover
        selected = choose_from(
            [g.name for g in goals],
            "Enter number",
        )  # pragma: no cover
        if selected is None:
            return  # pragma: no cover
        name = selected

    g = _find_goal(goals, name)
    if not g:
        goal_not_found(name, [g.name for g in goals])
        return
    # Confirm destructive operation unless --yes was supplied.
    if not yes and not click.confirm(
        f"Delete goal '{name}'?",
        default=False,
    ):
        return
    goals.remove(g)
    click.echo(f"[green]Deleted goal:[/] {name}")


@goal.command(name="notes", help="View or set notes for a goal.")
@click.argument("name")
@click.argument("text", required=False)
@with_goals
def goal_notes(name: str, text: Optional[str], goals: List[GoalArea]) -> None:
    """Display or update notes for ``name``."""
    g = _find_goal(goals, name)
    if not g:
        goal_not_found(name, [x.name for x in goals])
        return
    if text is None:
        click.echo(g.notes or "")
    else:
        g.notes = text.strip() or None
        click.echo(f"[green]Saved notes for '{name}'.")


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
    """Add a new phase under a goal."""
    # Prompt for the goal when not provided on the command line.
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            click.echo(
                "[red]No goals – use `loopbloom goal add`."
            )  # pragma: no cover
            return  # pragma: no cover
        click.echo(
            "Select goal for new phase:"
        )  # pragma: no cover
        goal_name = choose_from(
            names,
            "Enter number",
        )  # pragma: no cover
        if goal_name is None:
            return  # pragma: no cover

    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover
    # Avoid duplicates when the phase already exists.
    if _find_phase(g, phase_name):
        click.echo("[yellow]Phase exists.")
        return
    g.phases.append(Phase(name=phase_name.strip(), notes=notes or None))
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
    """Remove a phase from a goal."""
    # Ask which goal to operate on if not provided.
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            click.echo(
                "[red]No goals – use `loopbloom goal add`."
            )  # pragma: no cover
            return  # pragma: no cover
        click.echo(
            "Select goal:"
        )  # pragma: no cover
        goal_name = choose_from(
            names,
            "Enter number",
        )  # pragma: no cover
        if goal_name is None:
            return  # pragma: no cover

    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover

    # When no phase is specified, offer a menu of existing ones.
    if phase_name is None:
        options = [p.name for p in g.phases]
        if not options:
            click.echo(
                "[red]No phases found for this goal."
            )  # pragma: no cover
            return  # pragma: no cover
        click.echo(
            "Select phase to delete:"
        )  # pragma: no cover
        phase_name = choose_from(
            options,
            "Enter number",
        )  # pragma: no cover
        if phase_name is None:
            return  # pragma: no cover

    # Locate the phase object for deletion.
    p = _find_phase(g, phase_name)
    if not p:
        click.echo("[red]Phase not found.")  # pragma: no cover
        return  # pragma: no cover

    if not yes and not click.confirm(
        f"Delete phase '{phase_name}' from {goal_name}?",
        default=False,
    ):
        return
    g.phases.remove(p)
    click.echo(f"[green]Deleted phase '{phase_name}' from {goal_name}")


@phase.command(name="notes", help="View or set notes for a phase.")
@click.argument("goal_name")
@click.argument("phase_name")
@click.argument("text", required=False)
@with_goals
def phase_notes(
    goal_name: str,
    phase_name: str,
    text: Optional[str],
    goals: List[GoalArea],
) -> None:
    """Display or update notes for a phase."""
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])
        return
    p = _find_phase(g, phase_name)
    if not p:
        click.echo("[red]Phase not found.")
        return
    if text is None:
        click.echo(p.notes or "")
    else:
        p.notes = text.strip() or None
        click.echo(
            f"[green]Saved notes for phase '{phase_name}' under {goal_name}."
        )
