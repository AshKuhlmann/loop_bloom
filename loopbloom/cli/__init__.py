"""Helper decorators used by the command line interface.

This module contains small utilities shared across the various CLI
commands.  Keeping them here avoids repetition and keeps each command
implementation focused on its own behaviour.
"""

from functools import wraps
from typing import Any, Callable

import click


def with_goals(f: Callable[..., Any]) -> Callable[..., Any]:
    """Loads goals from the store in ``ctx.obj`` before running ``f``.

    The decorated command function receives a mutable list of
    :class:`~loopbloom.core.models.GoalArea` objects via the ``goals`` keyword
    argument. After the command completes, any modifications are persisted
    back to the underlying storage backend. This keeps individual commands
    simple and avoids repetitive load/save boilerplate across the CLI
    surface.
    """

    @wraps(f)
    @click.pass_context
    def wrapper(ctx: click.Context, /, *args: Any, **kwargs: Any) -> Any:
        # ``ctx.obj`` contains the application context created in ``__main__``.
        app = ctx.obj
        store = app.store
        # Load the entire goal graph before executing the command.
        goals = store.load()
        # ``f`` receives the list via the ``goals`` keyword argument so it can
        # mutate the collection in-place.
        result = f(*args, goals=goals, **kwargs)
        # Persist all changes once the command finishes unless dry-run is active.
        if not app.dry_run:
            store.save(goals)
        else:
            click.echo("[yellow]DRY RUN: Changes not saved.[/yellow]")
        return result

    return wrapper
