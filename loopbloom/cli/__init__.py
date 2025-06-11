"""CLI storage loader and saver for LoopBloom."""

from pathlib import Path  # noqa: F401
from typing import Any, Callable, List

import click

from loopbloom.core import config as cfg
from loopbloom.core.models import GoalArea
from loopbloom.storage.json_store import JSONStore
from loopbloom.storage.sqlite_store import SQLiteStore

store_backend = cfg.load().get("storage", "json")
STORE = SQLiteStore() if store_backend == "sqlite" else JSONStore()


def load_goals() -> List[GoalArea]:
    """Load and return all goal areas."""
    return STORE.load()


def save_goals(goals: List[GoalArea]) -> None:
    """Persist goal areas to disk."""
    STORE.save(goals)


def with_goals(f: Callable[..., Any]) -> Callable[..., Any]:
    """Load goals for ``f`` then save afterwards."""  # noqa: D401

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        goals = load_goals()
        result = f(*args, goals=goals, **kwargs)
        save_goals(goals)
        return result

    return click.pass_context(wrapper)
