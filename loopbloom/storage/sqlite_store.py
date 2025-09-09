"""SQLite implementation of :class:`~loopbloom.storage.base.Storage` using
SQLAlchemy Core for lightweight database access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    insert,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from loopbloom.constants import SQLITE_STORE_PATH
from loopbloom.core.models import GoalArea
from loopbloom.storage.base import Storage, StorageError

DEFAULT_PATH = SQLITE_STORE_PATH

metadata = MetaData()

# We store all data as a single JSON payload for simplicity. This keeps the
# schema trivial and avoids joins while the project is young.
raw_table = Table(
    "raw_json",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("payload", String, nullable=False),
)


class SQLiteStore(Storage):
    """Store goals in a single-row SQLite table."""

    def __init__(self, path: Path | str = DEFAULT_PATH):
        """Create a SQLite backed store.

        Args:
            path: Path to the SQLite database file.
        """
        path = Path(path)
        # Ensure parent directory exists before creating the engine/DB file.
        path.parent.mkdir(parents=True, exist_ok=True)
        self._path = path
        # ``future=True`` enables SQLAlchemy 2.0 style usage while remaining
        # compatible with older versions.
        self._engine: Engine = create_engine(f"sqlite:///{path}", future=True)
        # Create table schema if the DB file didn't exist yet.
        metadata.create_all(self._engine)

    def load(self) -> List[GoalArea]:
        """Load GoalAreas from the SQLite database."""
        try:
            with self._engine.begin() as conn:
                query = select(raw_table.c.payload)
                rows = conn.execute(query).scalars().all()
            if not rows:
                return []
            # Only one row is ever stored; deserialize its JSON payload.
            data = json.loads(rows[0])
            return [GoalArea.model_validate(obj) for obj in data]
        except SQLAlchemyError as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc

    def save(self, goals: List[GoalArea]) -> None:
        """Persist GoalAreas atomically."""
        payload = json.dumps([g.model_dump(mode="json") for g in goals])
        try:
            with self._engine.begin() as conn:
                # Replace the single row with the new payload.
                conn.execute(delete(raw_table))
                conn.execute(insert(raw_table).values(payload=payload))
        except SQLAlchemyError as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc

    def save_goal_area(self, goal: GoalArea) -> None:
        """Persist a single goal area back to the database."""
        goals = self.load()
        for i, g in enumerate(goals):
            if g.id == goal.id or g.name == goal.name:
                goals[i] = goal
                break
        else:
            goals.append(goal)
        self.save(goals)
