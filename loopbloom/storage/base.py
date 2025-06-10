"""Storage abstraction.

CLI, services, and core modules depend *only* on this protocol.
Concrete IO implementations should never leak into higher layers.
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

    def lock(self) -> ContextManager[None]:  # noqa: D401
        """Return an optional advisory lock (no-op by default)."""
        from contextlib import nullcontext

        return nullcontext()
