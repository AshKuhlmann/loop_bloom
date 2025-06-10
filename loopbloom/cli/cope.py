"""`loopbloom cope` command group."""

import click

from loopbloom.core.coping import PlanRepository, run_plan


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
