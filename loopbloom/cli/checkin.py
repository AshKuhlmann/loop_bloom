"""Daily check-in command.

This subcommand records progress for the active micro-habit under a goal
and offers a small pep talk to keep momentum going.
"""

import logging
from typing import List, Optional

import click
from rich import print

from loopbloom.cli import with_goals
from loopbloom.cli.interactive import interactive_select
from loopbloom.cli.utils import goal_not_found
from loopbloom.core.models import Checkin, GoalArea, MicroGoal, Status
from loopbloom.core.talks import TalkPool
from loopbloom.services.datetime import get_current_datetime
from loopbloom.services.progression import ProgressionService

logger = logging.getLogger(__name__)


@click.command(
    name="checkin",
    help="Record today’s success, skip, or failure for a goal.",
)
@click.argument("goal_name", required=False)
@click.option("--success/--skip", default=True, help="Mark success or skip.")
@click.option(
    "--fail",
    is_flag=True,
    default=False,
    help="Alias for --skip to record a failed check-in.",
)
@click.option("--note", default="", help="Optional note.")
@with_goals
def checkin(
    goal_name: Optional[str],
    success: bool,
    fail: bool,
    note: str,
    goals: List[GoalArea],
) -> None:
    """Append a ``Checkin`` to the active micro-goal.

    Args:
        goal_name: Name of the goal to check in for. When ``None`` an
            interactive selection is presented.
        success: Whether the check-in represents a success.
        fail: If ``True`` overrides ``success`` to record a failure/skip.
        note: Optional note stored with the check-in.
        goals: List of all goal areas loaded from storage.
    """
    # ``success`` picks the pep-talk mood. ``fail`` is merely an alias for
    # ``--skip`` and flips ``success`` when present. The optional ``note`` is
    # stored verbatim with the check-in.
    logger.debug("Starting check-in for goal_name=%s", goal_name)
    ctx = click.get_current_context()
    logger.debug("Dry run mode is %s", "ON" if ctx.obj.dry_run else "OFF")
    if ctx.obj.debug:
        click.echo(f"Dry run: {ctx.obj.dry_run}")
    if fail:
        success = False

    mg: MicroGoal | None = None
    goal: GoalArea | None = None
    today = get_current_datetime().date()
    logger.debug("Check-in date: %s", today)
    if ctx.obj.debug:
        click.echo(f"Check-in recorded for date: {today}")

    # If the user omitted a goal we ask interactively to ensure the check-in is
    # attributed to the correct micro-habit.
    if goal_name is None:
        if not goals:
            logger.error("No goals available for check-in")
            click.echo("[red]No goals – use `loopbloom goal add`.")
            return

        click.echo("Which goal do you want to check in for?")

        active: list[tuple[str, tuple[GoalArea, MicroGoal]]] = []
        for g in goals:
            for ph in g.phases:
                for m in ph.micro_goals:
                    if m.status is Status.active:
                        active.append((f"{g.name} -> {ph.name} -> {m.name}", (g, m)))
            for m in g.micro_goals:
                if m.status is Status.active:
                    active.append((f"{g.name} -> {m.name}", (g, m)))

        if not active:
            logger.info("No active micro-goals for interactive check-in")
            click.echo("No active micro-goals to check in for.")
            return

        selection = interactive_select(
            "Select a micro-goal to check in for",
            {label: pair for label, pair in active},
        )
        if selection is None:
            return

        goal, mg = selection
        goal_name = goal.name

    # Locate the goal by name if it wasn't selected interactively.
    if goal is None:
        goal = next(
            (g for g in goals if g.name.lower() == goal_name.lower()),
            None,
        )
        if not goal:
            logger.error("Goal not found: %s", goal_name)
            goal_not_found(goal_name, [g.name for g in goals])
            # No return here, let goal_not_found handle the exit
        # Once we know the goal, locate its currently active micro-habit so the
        # check-in updates the right place.
        mg = goal.get_active_micro_goal()

        if mg is None:
            logger.error("No active micro-goal in goal %s", goal.name)
            click.echo("[red]No active micro-goal found for this goal.")
            return

    assert mg is not None
    # Echo the chosen micro-habit so the user can confirm we recorded the
    # intended one.
    logger.info("Checking in for %s", mg.name)
    click.echo(f"Checking in for: [bold]{mg.name}[/bold]")
    # Append the new check-in so progress reports and streak calculations
    # include today's result.
    talk = TalkPool.random("success" if success else "skip")
    if success and "\u2713" not in talk:
        talk = "\u2713 " + talk
    ci = Checkin(
        date=today, success=success, note=note or None, self_talk_generated=talk
    )
    logger.debug("Check-in recorded for date: %s", today)
    mg.checkins.append(ci)

    # Output pep-talk so the user gets immediate encouragement.
    logger.info("Pep talk: %s", talk)
    print(talk)
    from loopbloom.core import config as cfg
    from loopbloom.services import notifier

    # Respect the user's preferred notification channel when sending the pep
    # talk.
    notify_mode = cfg.load().get("notify", "terminal")
    notifier.send("LoopBloom Check-in", talk, mode=notify_mode, goal=goal.name)

    progression_service = ProgressionService()
    should_progress, reasons = progression_service.check_progression(goal)

    if should_progress:
        print(
            "\n[bold green]Congratulations! You've made enough progress to "
            "advance to the next phase.[/bold green]"
        )
        for reason in reasons:
            print(f"- {reason}")
    else:
        # fmt: off
        progress_msg = (
            "\n[bold]Keep up the great work! You're making steady "
            "progress.[/bold]"
        )
        # fmt: on
        print(progress_msg)
        for reason in reasons:
            print(f"- {reason}")


checkin_cmd = checkin
