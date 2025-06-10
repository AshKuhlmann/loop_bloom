"""JSON-file implementation of Storage."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import ContextManager, List

from pydantic.json import pydantic_encoder

from loopbloom.core.models import GoalArea
from loopbloom.storage.base import Storage, StorageError

DEFAULT_PATH = Path(
    os.getenv("LOOPBLOOM_DATA_PATH", Path.home() / ".loopbloom" / "data.json")
)
DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)


class JSONStore(Storage):
    """Atomic JSON persistence."""

    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:  # noqa: D401
        """Initialise the store with the given file ``path``."""
        self._path = Path(path)

    def load(self) -> List[GoalArea]:  # noqa: D401
        """Return all goal areas from the backing JSON file."""
        if not self._path.exists():
            return []
        try:
            with self._path.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)
            return [GoalArea.model_validate(obj) for obj in raw]
        except Exception as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc

    def save(self, goals: List[GoalArea]) -> None:  # noqa: D401
        """Persist the entire goal graph atomically."""
        tmp_path: Path
        try:
            with NamedTemporaryFile(
                "w",
                delete=False,
                dir=self._path.parent,
            ) as tmp:
                json.dump(goals, tmp, default=pydantic_encoder, indent=2)
                tmp_path = Path(tmp.name)
            tmp_path.replace(self._path)
        except Exception as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc

    # Advisory lock not required for single-process Phase 1
    def lock(self) -> ContextManager[None]:
        """Return a no-op context manager for compatibility."""
        from contextlib import nullcontext

        return nullcontext()
