"""`loopbloom cope` command group."""

import click
import yaml

from loopbloom.core.coping import COPING_DIR, PlanRepository, run_plan


@click.group(name="cope", help="Guided coping workflows.")
def cope() -> None:
    """Coping subcommands."""
    pass


@cope.command(name="list", help="Show available coping plans.")
def _list() -> None:
    plans = PlanRepository.list_plans()
    for p in plans:
        click.echo(f"\u2022 {p.id} \u2013 {p.title}")


@cope.command(name="run", help="Run a coping plan by ID.")
@click.argument("plan_id")
def _run(plan_id: str) -> None:
    plan = PlanRepository.get(plan_id)
    if not plan:
        click.echo("[red]Plan not found. Use `loopbloom cope list`.")
        return
    click.echo(f"[cyan]{plan.title}[/cyan]")
    run_plan(plan)


@cope.command(name="new", help="Create a new coping plan interactively.")
def _new() -> None:
    """Prompt the user for plan details and save a YAML file."""
    plan_id = click.prompt("Plan ID (no spaces)").strip()
    if PlanRepository.get(plan_id):
        click.echo("[red]Plan already exists.")
        return
    title = click.prompt("Plan title").strip()
    click.echo("Add steps. Type 'p' for prompt, 'm' for message, 'q' to finish.")
    steps = []
    while True:
        kind = click.prompt("Step type", default="q").lower().strip()
        if kind.startswith("q"):
            break
        if kind.startswith("p"):
            prompt_text = click.prompt("Prompt text").strip()
            store = click.prompt(
                "Store answer as (blank for none)", default="", show_default=False
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
        click.echo("[red]No steps defined; aborting.")
        return
    content = {"id": plan_id, "title": title, "steps": steps}
    path = COPING_DIR / f"{plan_id}.yml"
    path.write_text(yaml.safe_dump(content, sort_keys=False, allow_unicode=True))
    click.echo(f"[green]Created plan:[/] {path}")
