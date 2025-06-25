"""CLI storage loader and saver for LoopBloom."""

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
        store = ctx.obj
        goals = store.load()
        result = f(*args, goals=goals, **kwargs)
        store.save(goals)
        return result

    return wrapper
