"""LoopBloom CLI: goal, phase, and micro-habit CRUD."""

from typing import List, Optional

import click

from loopbloom.cli import with_goals
from loopbloom.cli.interactive import choose_from
from loopbloom.core.models import GoalArea, MicroGoal, Phase, Status


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
def goal_add(ctx: click.Context, name: str, goals: List[GoalArea]) -> None:
    """Add a new goal area."""
    if _find_goal(goals, name):
        click.echo("[yellow]Goal already exists.")
        return
    goals.append(GoalArea(name=name.strip()))
    click.echo(f"[green]Added goal:[/] {name}")


@goal.command(name="list")
@with_goals
def goal_list(ctx: click.Context, goals: List[GoalArea]) -> None:
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
    ctx: click.Context,
    name: Optional[str],
    yes: bool,
    goals: List[GoalArea],
) -> None:
    """Remove a goal area."""
    if name is None:
        if not goals:
            click.echo("[italic]No goals – nothing to remove.")
            return
        click.echo("Which goal do you want to delete?")
        selected = choose_from([g.name for g in goals], "Enter number")
        if selected is None:
            return
        name = selected

    g = _find_goal(goals, name)
    if not g:
        click.echo("[red]Goal not found.")
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
    ctx: click.Context,
    goal_name: Optional[str],
    phase_name: str,
    goals: List[GoalArea],
) -> None:
    """Add a new phase under a goal."""
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            click.echo("[red]No goals – use `loopbloom goal add`.")
            return
        click.echo("Select goal for new phase:")
        goal_name = choose_from(names, "Enter number")
        if goal_name is None:
            return

    g = _find_goal(goals, goal_name)
    if not g:
        click.echo("[red]Goal not found.")
        return
    if _find_phase(g, phase_name):
        click.echo("[yellow]Phase exists.")
        return
    g.phases.append(Phase(name=phase_name.strip()))
    click.echo(f"[green]Added phase '{phase_name}' to {goal_name}")


# Micro commands
@goal.group(name="micro", help="Micro-habit commands.")
def micro() -> None:
    """Micro-habit subcommands."""
    pass


@micro.command(name="add")
@click.argument("goal_name", required=False)
@click.argument("phase_name", required=False)
@click.argument("micro_name")
@with_goals
def micro_add(
    ctx: click.Context,
    goal_name: Optional[str],
    phase_name: Optional[str],
    micro_name: str,
    goals: List[GoalArea],
) -> None:
    """Add a micro-habit to a phase."""
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            click.echo("[red]No goals – use `loopbloom goal add`.")
            return
        click.echo("Select goal for new micro-habit:")
        goal_name = choose_from(names, "Enter number")
        if goal_name is None:
            return

    g = _find_goal(goals, goal_name)
    if phase_name is None:
        if not g:
            click.echo("[red]Goal not found.")
            return
        options = [p.name for p in g.phases]
        if not options:
            click.echo("[red]No phases found for this goal.")
            return
        click.echo("Select phase:")
        phase_name = choose_from(options, "Enter number")
        if phase_name is None:
            return

    p = _find_phase(g, phase_name) if g else None
    if not p:
        if g and phase_name.lower() == "default":
            p = Phase(name=phase_name.strip())
            g.phases.append(p)
        else:
            click.echo("[red]Goal or phase not found.")
            return
    p.micro_goals.append(MicroGoal(name=micro_name.strip()))
    message = (
        "[green]Added micro-habit '"
        + micro_name
        + "' to "
        + goal_name
        + "/"
        + phase_name
    )
    click.echo(message)


@micro.command(name="cancel")
@click.argument("goal_name", required=False)
@click.argument("phase_name", required=False)
@click.argument("micro_name", required=False)
@with_goals
def micro_cancel(
    ctx: click.Context,
    goal_name: Optional[str],
    phase_name: Optional[str],
    micro_name: Optional[str],
    goals: List[GoalArea],
) -> None:
    """Soft-delete (cancel) a micro-habit."""
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            click.echo("[red]No goals – use `loopbloom goal add`.")
            return
        click.echo("Select goal:")
        goal_name = choose_from(names, "Enter number")
        if goal_name is None:
            return

    g = _find_goal(goals, goal_name)
    if phase_name is None:
        if not g:
            click.echo("[red]Goal not found.")
            return
        options = [p.name for p in g.phases]
        if not options:
            click.echo("[red]No phases found for this goal.")
            return
        click.echo("Select phase:")
        phase_name = choose_from(options, "Enter number")
        if phase_name is None:
            return

    p = _find_phase(g, phase_name) if g else None
    if not p:
        click.echo("[red]Goal or phase not found.")
        return

    if micro_name is None:
        options = [m.name for m in p.micro_goals if m.status == Status.active]
        if not options:
            click.echo("[red]No active micro-habits in this phase.")
            return
        click.echo("Select micro-habit:")
        micro_name = choose_from(options, "Enter number")
        if micro_name is None:
            return

    mg = next((m for m in p.micro_goals if m.name == micro_name), None)
    if not mg:
        click.echo("[red]Micro-habit not found.")
        return
    mg.status = Status.cancelled
    click.echo(f"[yellow]Cancelled micro-habit:[/] {micro_name}")
