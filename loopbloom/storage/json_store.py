"""JSON-file implementation of :class:`~loopbloom.storage.base.Storage`.

Goals are serialized to a single JSON document on disk making this backend
easy to inspect and backup.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import ContextManager, List

from pydantic.json import pydantic_encoder

from loopbloom.constants import JSON_DEFAULT_PATH
from loopbloom.core.models import GoalArea
from loopbloom.storage.base import Storage, StorageError

logger = logging.getLogger(__name__)

DEFAULT_PATH = JSON_DEFAULT_PATH


class JSONStore(Storage):
    """Atomic JSON persistence."""

    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:  # noqa: D401
        """Initialise the store with the given file ``path``."""
        self._path = Path(path)

    def load(self) -> List[GoalArea]:  # noqa: D401
        """Return all goal areas from the backing JSON file."""
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

    def save(self, goals: List[GoalArea]) -> None:  # noqa: D401
        """Persist the entire goal graph atomically."""
        logger.debug("Saving %d goals to %s", len(goals), self._path)
        tmp_path: Path
        try:
            with NamedTemporaryFile(
                "w",
                delete=False,
                dir=self._path.parent,
            ) as tmp:
                # Write to a temp file then rename for atomicity.
                # ``delete=False`` ensures Windows compatibility.
                json.dump(goals, tmp, default=pydantic_encoder, indent=2)
                tmp_path = Path(tmp.name)
            tmp_path.replace(self._path)
            logger.debug("Save successful")
        except Exception as exc:  # pragma: no cover
            logger.error("Error saving %s: %s", self._path, exc)
            raise StorageError(str(exc)) from exc

    def save_goal_area(self, goal: GoalArea) -> None:
        """Update or append a single goal area."""
        goals = self.load()
        for i, g in enumerate(goals):
            if g.id == goal.id or g.name == goal.name:
                goals[i] = goal
                break
        else:
            goals.append(goal)
        self.save(goals)

    # Advisory lock not required for single-process Phase 1
    def lock(self) -> ContextManager[None]:
        """Return a no-op context manager for compatibility."""
        from contextlib import nullcontext

        # JSON files don't need locking in single-user mode.
        return nullcontext()
