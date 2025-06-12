"""Daily check-in command."""

from typing import List

import click
from rich import print

from loopbloom.cli import with_goals
from loopbloom.core.models import Checkin, GoalArea
from loopbloom.core.talks import TalkPool


@click.command(
    name="checkin",
    help="Record today’s success or skip for a goal.",
)
@click.argument("goal_name", required=False)
@click.option("--goal", "goal_opt", help="Goal name (alternative to argument).")
@click.option(
    "--status",
    type=click.Choice(["done", "skip"]),
    help="Mark success or skip via status value.",
)
@click.option("--success/--skip", "success_flag", default=True, help="Mark success or skip.")
@click.option("--note", default="", help="Optional note.")
@with_goals
def checkin(
    ctx: click.Context,
    goal_name: str | None,
    goal_opt: str | None,
    status: str | None,
    success_flag: bool,
    note: str,
    goals: List[GoalArea],
) -> None:
    """Append a Checkin to the current active micro-goal of GOAL_NAME."""
    # Determine final goal name
    goal_name = goal_opt or goal_name
    if not goal_name:
        click.echo("[red]Goal required.")
        return

    # Determine success flag
    success = success_flag
    if status is not None:
        success = status == "done"

    # Locate goal
    goal = next(
        (g for g in goals if g.name.lower() == goal_name.lower()),
        None,
    )
    if not goal:
        click.echo("[red]Goal not found.")
        return
    # Find first phase with an active micro-goal
    mg = None
    for ph in goal.phases:
        mg = next((m for m in ph.micro_goals if m.status == "active"), None)
        if mg:
            break
    if mg is None:
        click.echo("[red]No active micro-goal found for this goal.")
        return
    # Create check-in
    talk = TalkPool.random("success" if success else "skip")
    if success and "\u2713" not in talk:
        talk = "\u2713 " + talk
    ci = Checkin(success=success, note=note or None, self_talk_generated=talk)
    mg.checkins.append(ci)

    # Output pep-talk
    print(talk)
    from loopbloom.core import config as cfg
    from loopbloom.services import notifier

    notify_mode = cfg.load().get("notify", "terminal")
    notifier.send("LoopBloom Check-in", talk, mode=notify_mode)
