"""Storage abstraction shared across persistence backends.

CLI, services and core modules depend solely on this small protocol to
keep the rest of the codebase decoupled from the underlying storage
mechanism.
"""

from __future__ import annotations

from typing import ContextManager, List, Protocol

from loopbloom.core.models import GoalArea


class StorageError(RuntimeError):
    """Raised on IO failures."""


class Storage(Protocol):
    """Persistence interface."""

    def load(self) -> List[GoalArea]:
        """Return all goal areas from disk (or remote).

        Implementations must raise ``StorageError`` on unrecoverable errors and
        return ``[]`` on first-run or if the data file is missing.
        """

    def save(self, goals: List[GoalArea]) -> None:  # noqa: D401
        """Persist full graph atomically."""

    def save_goal_area(self, goal: GoalArea) -> None:
        """Persist a single goal area."""

    def lock(self) -> ContextManager[None]:  # noqa: D401
        """Return an optional advisory lock (no-op by default)."""
        from contextlib import nullcontext
        # Single-user mode doesn't require locking, so we return a context
        # manager that does nothing. Back-ends dealing with concurrent writes
        # can override this to provide real locking semantics.
        return nullcontext()
