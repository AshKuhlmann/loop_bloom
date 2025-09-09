"""JSON-file implementation of :class:`~loopbloom.storage.base.Storage`.

Goals are serialized to a single JSON document on disk making this backend
easy to inspect and backup.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, ContextManager, Iterable, List

from loopbloom.constants import JSON_STORE_PATH
from loopbloom.core.models import GoalArea
from loopbloom.storage.base import Storage, StorageError

logger = logging.getLogger(__name__)

DEFAULT_PATH = JSON_STORE_PATH


class JSONStore(Storage):
    """Atomic JSON persistence."""

    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:  # noqa: D401
        """Create a new JSON store instance.

        Args:
            path: Location of the JSON file used for persistence.
        """
        self._path = Path(path)

    def load(self) -> List[GoalArea]:  # noqa: D401
        """Load goal areas from the JSON data file.

        Returns:
            list[GoalArea]: All stored goal areas, or an empty list when the
            file does not exist.
        """
        logger.debug("Loading goals from %s", self._path)
        if not self._path.exists():
            logger.debug("Data file not found; returning empty list")
            # First run or missing data file -> treat as empty.
            return []
        try:
            with self._path.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)
            goals = [GoalArea.model_validate(obj) for obj in raw]
            logger.debug("Loaded %d goal areas", len(goals))
            return goals
        except Exception as exc:  # pragma: no cover
            logger.error("Error loading %s: %s", self._path, exc)
            raise StorageError(str(exc)) from exc

    def save(self, goals: List[GoalArea]) -> None:
        """Persist the entire goal graph atomically."""
        logger.debug("Saving %d goals to %s", len(goals), self._path)
        try:
            # Ensure parent directory exists before writing.
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as fp:
                # Use Pydantic v2 JSON-mode dump to serialize dates/datetimes.
                payload: Iterable[dict[str, Any]] = (
                    g.model_dump(mode="json") for g in goals
                )
                json.dump(list(payload), fp, indent=2)
            logger.debug("Save successful")
        except Exception as exc:  # pragma: no cover
            logger.error("Error saving %s: %s", self._path, exc)
            raise StorageError(str(exc)) from exc

    def save_goal_area(self, goal: GoalArea) -> None:
        """Persist a single goal area by updating or appending it."""
        goals = self.load()
        logger.debug(f"Saving goal: {goal.name} (ID: {goal.id})")
        found = False
        for i, g in enumerate(goals):
            logger.debug(f"  Comparing with existing goal: {g.name} (ID: {g.id})")
            if g.id == goal.id:
                logger.debug(f"    Match by ID: {g.id}")
                goals[i] = goal
                found = True
                break
        if not found:
            logger.debug(f"  No match found, appending new goal: {goal.name}")
            goals.append(goal)
        self.save(goals)

    # Advisory lock not required for single-process Phase 1
    def lock(self) -> ContextManager[None]:
        """Return an empty context manager when locking isn't required."""
        from contextlib import nullcontext

        # JSON files don't need locking in single-user mode.
        return nullcontext()
