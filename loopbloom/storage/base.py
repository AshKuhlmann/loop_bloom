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
        """Load every goal area from persistent storage.

        Implementations may read from local files or remote services. A
        :class:`StorageError` should be raised for unrecoverable failures while
        a missing data file should simply result in an empty list.

        Returns:
            list[GoalArea]: Parsed goal areas from the backend.
        """

    def save(self, goals: List[GoalArea]) -> None:  # noqa: D401
        """Persist the entire goal graph in one operation."""

    def save_goal_area(self, goal: GoalArea) -> None:
        """Update or append ``goal`` in storage."""

    def lock(self) -> ContextManager[None]:  # noqa: D401
        """Return an advisory lock if the backend supports it."""
        from contextlib import nullcontext

        # Single-user mode doesn't require locking, so we return a context
        # manager that does nothing. Back-ends dealing with concurrent writes
        # can override this to provide real locking semantics.
        return nullcontext()
