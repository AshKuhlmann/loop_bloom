"""CLI commands for micro-habit lifecycle management."""

import logging
from typing import List, Optional, Tuple

import click

from loopbloom.cli import with_goals
from loopbloom.cli.interactive import choose_from
from loopbloom.cli.utils import find_goal, find_phase, goal_not_found
from loopbloom.core.models import GoalArea, MicroGoal, Phase, Status
from loopbloom.storage.base import Storage as DataStore

logger = logging.getLogger(__name__)


def _get_or_select_phase(
    storage: DataStore, goal_name: str, phase_name: Optional[str]
) -> Optional[Phase]:
    """Return the desired phase, prompting when needed."""
    goals = storage.load()
    goal = find_goal(goals, goal_name)
    if not goal:
        goal_not_found(goal_name, [g.name for g in goals])
        return None
    if phase_name:
        return find_phase(goal, phase_name)
    if not goal.phases:
        return None
    click.echo("Select phase:")
    choice = choose_from([p.name for p in goal.phases], "Enter number")
    if choice is None:
        return None
    return find_phase(goal, choice)


def _prompt_for_new_micro_goal() -> str:
    """Ask user for a micro-habit name."""
    # ``click.prompt`` returns ``Any`` due to loose typing, so cast to ``str``
    # before stripping whitespace for strict type checking.
    from typing import cast

    return cast(str, click.prompt("Micro-habit name")).strip()


def _get_or_select_micro_goal(
    storage: DataStore,
    goal_name: str,
    phase_name: Optional[str],
    micro_goal_name: Optional[str],
) -> Optional[Tuple[Phase, MicroGoal]]:
    """Locate a micro-goal, asking the user when needed."""
    phase = _get_or_select_phase(storage, goal_name, phase_name)
    if phase is None:
        if phase_name:
            return None
        goals = storage.load()
        goal = find_goal(goals, goal_name)
        if not goal:
            return None
        target_list = goal.micro_goals
    else:
        target_list = phase.micro_goals
    if micro_goal_name:
        mg = next(
            (m for m in target_list if m.name.lower() == micro_goal_name.lower()),
            None,
        )
    else:
        options = [m.name for m in target_list]
        if not options:
            return None
        click.echo("Select micro-habit:")
        choice = choose_from(options, "Enter number")
        if choice is None:
            return None
        mg = next((m for m in target_list if m.name == choice), None)
    if mg is None:
        return None
    if phase is None:
        phase = Phase(name="")
        phase.micro_goals = target_list
    return phase, mg


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
    # Find the goal so we update the correct part of the hierarchy.
    g = find_goal(goals, goal_name)
    if not g:
        logger.error("Goal not found for micro complete: %s", goal_name)
        goal_not_found(goal_name, [x.name for x in goals])
        return

    target_list: List[MicroGoal]
    if phase_name:
        # Restrict the search to the specified phase when one is given.
        p = find_phase(g, phase_name)
        if not p:
            logger.error(
                "Phase not found for micro complete: %s/%s",
                goal_name,
                phase_name,
            )
            click.echo(f"[red]Phase '{phase_name}' not found.")
            return
        target_list = p.micro_goals
    else:
        # Without a phase we look at micro-habits attached directly to the
        # goal itself.
        target_list = g.micro_goals

    # Accept case-insensitive names so the command is forgiving of user input.
    mg = next((m for m in target_list if m.name.lower() == name.lower()), None)
    if not mg:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        logger.error("Micro-habit not found: %s in %s", name, loc)
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return

    # Update the status immediately so subsequent commands reflect the change.
    mg.status = Status.complete
    logger.info("Marked micro-habit %s complete", name)
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
    # Find the owning goal so we modify the right micro-habit.
    g = find_goal(goals, goal_name)
    if not g:
        logger.error("Goal not found for micro cancel: %s", goal_name)
        goal_not_found(goal_name, [x.name for x in goals])
        return

    target_list: List[MicroGoal]
    if phase_name:
        # Only look inside the given phase when the user specifies one.
        p = find_phase(g, phase_name)
        if not p:
            logger.error(
                "Phase not found for micro cancel: %s/%s",
                goal_name,
                phase_name,
            )
            click.echo(f"[red]Phase '{phase_name}' not found.")
            return
        target_list = p.micro_goals
    else:
        # If no phase is specified check the micro-habits attached directly to
        # the goal.
        target_list = g.micro_goals

    mg = next((m for m in target_list if m.name.lower() == name.lower()), None)
    if not mg:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        logger.error("Micro-habit not found for cancel: %s in %s", name, loc)
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return

    # Cancel the habit but keep its check-in history for future reference.
    mg.status = Status.cancelled
    logger.info("Cancelled micro-habit %s", name)
    click.echo(f"[green]Cancelled micro-habit '{name}'.")


@micro.command(name="add")
@click.argument("name", required=False)
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
    name: Optional[str],
    goal_name: Optional[str],
    phase_name: Optional[str],
    goals: List[GoalArea],
) -> None:
    """Add a new micro-habit to a goal or phase.

    If ``goal_name`` is omitted, the user is prompted to select one.
    If ``phase_name`` is provided but doesn't exist, a new phase will be
    created automatically.
    """
    # When the user doesn't specify a goal we prompt them so the new micro-habit
    # ends up attached to the intended place.
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            logger.error("No goals available for micro add")
            click.echo("[red]No goals – use `loopbloom goal add`.")
            raise click.Abort()
        click.echo("Select goal for new micro-habit:")
        logger.info("Prompting for goal selection for micro add")
        goal_name = choose_from(names, "Enter number")
        if goal_name is None:
            return

    # Look up the goal to verify it exists before we try to add anything to it.
    g = find_goal(goals, goal_name)
    if not g:
        logger.error("Goal not found for micro add: %s", goal_name)
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        raise click.Abort()  # pragma: no cover

    ctx = click.get_current_context()
    store = ctx.obj.store

    target_phase = _get_or_select_phase(store, goal_name, phase_name)
    if phase_name and target_phase is None:
        target_phase = Phase(name=phase_name.strip())
        g.phases.append(target_phase)
        logger.info("Created phase %s under %s", phase_name, goal_name)
        click.echo(f"[yellow]Created phase '{phase_name}' under goal '{goal_name}'.")
    elif target_phase is not None:
        target_phase = find_phase(g, target_phase.name) or target_phase

    if name is None:
        name = _prompt_for_new_micro_goal()
    else:
        name = name.strip()

    if target_phase is None:
        g.micro_goals.append(MicroGoal(name=name))
        click.echo(f"[green]Added micro-habit '{name}' to goal '{goal_name}'")
    else:
        target_phase.micro_goals.append(MicroGoal(name=name))
        click.echo(
            (
                f"[green]Added micro-habit '{name}' to {goal_name}/"
                f"{target_phase.name}"
            )
        )

    store.save_goal_area(g)
    logger.info("Added micro-habit %s", name)


@micro.command(name="rm")
@click.argument("name", required=False)
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
    name: Optional[str],
    goal_name: str,
    phase_name: Optional[str],
    yes: bool,
    goals: List[GoalArea],
) -> None:
    """Remove a micro-habit by its name."""
    # Ensure the command targets a valid goal before proceeding.
    g = find_goal(goals, goal_name)
    if not g:
        logger.error("Goal not found for micro rm: %s", goal_name)
        goal_not_found(goal_name, [x.name for x in goals])  # pragma: no cover
        return  # pragma: no cover

    if phase_name and not find_phase(g, phase_name):
        click.echo(f"[red]Phase '{phase_name}' not found.")
        return

    result = _get_or_select_micro_goal(
        click.get_current_context().obj.store,
        goal_name,
        phase_name,
        name,
    )
    if not result:
        loc = f"phase '{phase_name}'" if phase_name else f"goal '{goal_name}'"
        click.echo(f"[red]Micro-habit '{name}' not found in {loc}.")
        return
    p, mg = result

    if not yes and not click.confirm(
        f"Permanently delete '{mg.name}'?",
        default=False,
    ):
        return

    if phase_name:
        tgt_phase = find_phase(g, p.name) or p
        target_list = tgt_phase.micro_goals
    else:
        target_list = g.micro_goals
    mg_actual = next(
        (m for m in target_list if m.name.lower() == mg.name.lower()),
        None,
    )
    if mg_actual is None:
        click.echo(f"[red]Micro-habit '{mg.name}' not found in {goal_name}.")
        return

    target_list.remove(mg_actual)
    ctx = click.get_current_context()
    ctx.obj.store.save_goal_area(g)
    logger.info("Deleted micro-habit %s", mg.name)
    click.echo(f"[green]Deleted micro-habit:[/] {mg.name}")


micro_cmd = micro
