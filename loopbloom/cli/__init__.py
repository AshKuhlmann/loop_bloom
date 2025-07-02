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
        # The root ``cli`` command stores the chosen persistence backend in
        # ``ctx.obj`` so every subcommand can access it without re-reading
        # configuration files.
        store = ctx.obj
        # Load the entire goal graph before executing the command.
        goals = store.load()
        # ``f`` receives the list via the ``goals`` keyword argument so it can
        # mutate the collection in-place.
        result = f(*args, goals=goals, **kwargs)
        # Persist all changes once the command finishes.
        store.save(goals)
        return result

    return wrapper
