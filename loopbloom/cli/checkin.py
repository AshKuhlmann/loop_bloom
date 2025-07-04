"""Daily check-in command.

This subcommand records progress for the active micro-habit under a goal
and offers a small pep talk to keep momentum going.
"""

import logging
from typing import List, Optional

import click
from rich import print

from loopbloom.cli import with_goals
from loopbloom.cli.interactive import choose_from
from loopbloom.cli.utils import goal_not_found
from loopbloom.core.models import Checkin, GoalArea
from loopbloom.core.talks import TalkPool
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
    """Append a Checkin to the current active micro-goal of ``GOAL_NAME``.

    When ``goal_name`` is omitted, the command interactively asks which
    goal to check in for.
    """
    # ``success`` determines which pep-talk pool we draw from. ``note`` is an
    # optional free-form comment stored alongside the check-in. ``fail`` is an
    # alias for ``--skip`` and overrides ``success`` when provided.
    if fail:
        success = False
    # If the user did not specify which goal to log, prompt with a list.
    if goal_name is None:
        names = [g.name for g in goals]
        if not names:
            logger.error("No goals available for check-in")
            click.echo("[red]No goals – use `loopbloom goal add`.")
            return
        click.echo("Which goal do you want to check in for?")
        logger.info("Prompting for goal selection")
        goal_name = choose_from(names, "Enter number")
        if goal_name is None:
            return

    # Locate the goal by name (case-insensitive) from the loaded list.
    goal = next(
        (g for g in goals if g.name.lower() == goal_name.lower()),
        None,
    )
    if not goal:
        logger.error("Goal not found: %s", goal_name)
        goal_not_found(goal_name, [g.name for g in goals])
        return
    # Find the active micro-goal
    mg = goal.get_active_micro_goal()

    if mg is None:
        logger.error("No active micro-goal in goal %s", goal.name)
        click.echo("[red]No active micro-goal found for this goal.")
        return
    # Inform the user which micro-habit is being checked in
    logger.info("Checking in for %s", mg.name)
    click.echo(f"Checking in for: [bold]{mg.name}[/bold]")
    # Create check-in object and attach to the micro-goal.
    talk = TalkPool.random("success" if success else "skip")
    if success and "\u2713" not in talk:
        talk = "\u2713 " + talk
    ci = Checkin(success=success, note=note or None, self_talk_generated=talk)
    mg.checkins.append(ci)

    # Output pep-talk so the user gets immediate encouragement.
    logger.info("Pep talk: %s", talk)
    print(talk)
    from loopbloom.core import config as cfg
    from loopbloom.services import notifier

    # Notification style (desktop or terminal) comes from user config.
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
        print(
            "\n[bold]Keep up the great work! You're making steady "
            "progress.[/bold]"
        )
        for reason in reasons:
            print(f"- {reason}")
