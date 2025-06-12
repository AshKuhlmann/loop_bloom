"""Daily check-in command."""

@click.option(
    "--goal",
    "goal_opt",
    help="Goal name (alternative to argument).",
)
@click.option(
    "--success/--skip",
    "success_flag",
    default=True,
    help="Mark success or skip.",
)
import click
from rich import print

from loopbloom.cli import with_goals
from loopbloom.cli.interactive import choose_from
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
    goal_name: Optional[str],
    goal_opt: Optional[str],
    status: Optional[str],
    success_flag: bool,
    note: str,
    goals: List[GoalArea],
) -> None:
    """Append a Checkin to the current active micro-goal of GOAL_NAME."""
    # Determine final goal name from options, or fall back to interactive prompt
    final_goal_name = goal_opt or goal_name
    if not final_goal_name:
        names = [g.name for g in goals]
        if not names:
            click.echo("[red]No goals – use `loopbloom goal add`.")
            return
        click.echo("Which goal do you want to check in for?")
        final_goal_name = choose_from(names, "Enter number")
        if final_goal_name is None:
            return

    # Determine success flag
    success = success_flag
    if status is not None:
        success = status == "done"

    # Locate goal
    goal = next(
        (g for g in goals if g.name.lower() == final_goal_name.lower()),
        None,
    )
    if not goal:
        click.echo(f"[red]Goal '{final_goal_name}' not found.")
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