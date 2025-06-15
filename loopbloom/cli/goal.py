"""LoopBloom CLI: goal, phase, and micro-habit CRUD."""

from typing import List, Optional

import click

from loopbloom.cli import with_goals
from loopbloom.cli.utils import goal_not_found
from loopbloom.cli.interactive import choose_from
from loopbloom.core.models import GoalArea, MicroGoal, Phase


def _find_goal(goals: List[GoalArea], name: str) -> Optional[GoalArea]:
    """Return the goal matching ``name`` if present."""
    return next((g for g in goals if g.name.lower() == name.lower()), None)


def _find_phase(goal: GoalArea, name: str) -> Optional[Phase]:
    """Return phase from ``goal`` matching ``name`` if found."""
    return next(
        (p for p in goal.phases if p.name.lower() == name.lower()),
        None,
    )


@click.group(name="goal", help="Manage goals, phases, and micro-habits.")
def goal() -> None:
    """Goal-level commands."""
    pass


@goal.command(name="add")
@click.argument("name")
@with_goals
def goal_add(name: str, goals: List[GoalArea]) -> None:
    """Add a new goal area."""
    if _find_goal(goals, name):
        click.echo("[yellow]Goal already exists.")
        return
    goals.append(GoalArea(name=name.strip()))
    click.echo(f"[green]Added goal:[/] {name}")


@goal.command(name="list")
@with_goals
def goal_list(goals: List[GoalArea]) -> None:
    """List all goal areas."""
    if not goals:
        click.echo("[italic]No goals – use `loopbloom goal add`.")
        return
    for g in goals:
        click.echo(f"• {g.name} (phases: {len(g.phases)})")


@goal.command(name="rm")
@click.argument("name", required=False)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
@with_goals
def goal_rm(
    name: Optional[str],
    yes: bool,
    goals: List[GoalArea],
) -> None:
    """Remove a goal area."""
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
    if not yes and not click.confirm(
        f"Delete goal '{name}'?",
        default=False,
    ):
        return
    goals.remove(g)
    click.echo(f"[green]Deleted goal:[/] {name}")


# Phase commands
@goal.group(name="phase", help="Phase-level commands.")
def phase() -> None:
    """Phase-level subcommands."""
    pass


@phase.command(name="add")
@click.argument("goal_name", required=False)
@click.argument("phase_name")
@with_goals
def phase_add(
    goal_name: Optional[str],
    phase_name: str,
    goals: List[GoalArea],
) -> None:
    """Add a new phase under a goal."""
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
    if _find_phase(g, phase_name):
        click.echo("[yellow]Phase exists.")
        return
    g.phases.append(Phase(name=phase_name.strip()))
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


# Micro commands
@goal.group(name="micro", help="Micro-habit commands.")
def micro() -> None:
    """Micro-habit subcommands."""
    pass


@micro.command(name="add")
@click.argument("name")
@click.option(
    "--goal",
    "goal_name",
    required=True,
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
    goal_name: str,
    phase_name: Optional[str],
    goals: List[GoalArea],
) -> None:
    """Add a new micro-habit to a goal or phase.

    If ``phase_name`` is provided but doesn't exist, a new phase will be
    created automatically.
    """
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover

    if phase_name is None:
        g.micro_goals.append(MicroGoal(name=name.strip()))
        click.echo(f"[green]Added micro-habit '{name}' to goal '{goal_name}'")
        return

    p = _find_phase(g, phase_name)
    if not p:
        p = Phase(name=phase_name.strip())
        g.phases.append(p)
        click.echo(
            f"[yellow]Created phase '{phase_name}' under goal '{goal_name}'."
        )
    p.micro_goals.append(MicroGoal(name=name.strip()))
    click.echo(
        f"[green]Added micro-habit '{name}' to {goal_name}/{phase_name}"
    )


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
    g = _find_goal(goals, goal_name)
    if not g:
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover

    target_list: Optional[List[MicroGoal]] = None
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

    if not yes and not click.confirm(
        f"Permanently delete '{name}'?", default=False
    ):
        return

    target_list.remove(mg)
    click.echo(f"[green]Deleted micro-habit:[/] {name}")
