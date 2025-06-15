"""CLI storage loader and saver for LoopBloom."""

from functools import wraps
from typing import Any, Callable

import click


def with_goals(f: Callable[..., Any]) -> Callable[..., Any]:
    """Loads goals from the store in ctx.obj, then saves after."""

    @wraps(f)
    @click.pass_context
    def wrapper(ctx: click.Context, /, *args: Any, **kwargs: Any) -> Any:
        store = ctx.obj
        goals = store.load()
        result = f(*args, goals=goals, **kwargs)
        store.save(goals)
        return result

    return wrapper
