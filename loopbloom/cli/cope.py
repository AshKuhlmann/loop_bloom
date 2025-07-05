"""`loopbloom cope` command group.

These commands provide guided workflows for dealing with stressful or
overwhelming situations. Plans are defined in YAML so users can add their
own customised coping strategies.
"""

import logging

import click
import yaml

from loopbloom.constants import COPING_DIR
from loopbloom.core.coping import PlanRepository, run_plan

logger = logging.getLogger(__name__)


@click.group(name="cope", help="Guided coping workflows.")
def cope() -> None:
    """Coping subcommands."""
    pass


@cope.command(name="list", help="Show available coping plans.")
def _list() -> None:
    # Show all YAML plans bundled or created by the user.
    plans = PlanRepository.list_plans()
    logger.info("Listing coping plans")
    for p in plans:
        click.echo(f"\u2022 {p.id} \u2013 {p.title}")


@cope.command(name="run", help="Run a coping plan by ID.")
@click.argument("plan_id")
def _run(plan_id: str) -> None:
    # Load the requested plan from disk.
    plan = PlanRepository.get(plan_id)
    if not plan:
        logger.error("Plan not found: %s", plan_id)
        click.echo("[red]Plan not found. Use `loopbloom cope list`.")
        return
    logger.info("Running plan %s", plan_id)
    click.echo(f"[cyan]{plan.title}[/cyan]")
    run_plan(plan)


@cope.command(name="new", help="Create a new coping plan interactively.")
def _new() -> None:
    """Prompt the user for plan details and save a YAML file."""
    plan_id = click.prompt("Plan ID (no spaces)").strip()
    if PlanRepository.get(plan_id):
        logger.error("Plan already exists: %s", plan_id)
        click.echo("[red]Plan already exists.")
        return
    title = click.prompt("Plan title").strip()
    # Inform the user how to add interactive steps to the plan.
    msg = "Add steps. Type 'p' for prompt, 'm' for message, 'q' to finish."
    click.echo(msg)
    steps = []
    # Steps are collected interactively until the user chooses to quit.
    while True:
        kind = click.prompt("Step type", default="q").lower().strip()
        if kind.startswith("q"):
            break
        if kind.startswith("p"):
            prompt_text = click.prompt("Prompt text").strip()
            store = click.prompt(
                "Store answer as (blank for none)",
                default="",
                show_default=False,
            ).strip()
            step = {"prompt": prompt_text}
            if store:
                step["store_as"] = store
            steps.append(step)
        elif kind.startswith("m"):
            message = click.prompt("Message text").strip()
            steps.append({"message": message})
        else:
            click.echo("Use 'p', 'm', or 'q'.")
    if not steps:
        logger.error("No steps defined for new plan")
        click.echo("[red]No steps defined; aborting.")
        return
    content = {"id": plan_id, "title": title, "steps": steps}
    path = COPING_DIR / f"{plan_id}.yml"
    dumped = yaml.safe_dump(content, sort_keys=False, allow_unicode=True)
    path.write_text(dumped)
    # Show full path so users know where the YAML file lives
    # and can edit it manually if desired.
    logger.info("Created plan %s", path)
    click.echo(f"[green]Created plan:[/] {path}")
