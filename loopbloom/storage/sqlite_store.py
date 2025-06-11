"""SQLite implementation of Storage using SQLAlchemy Core."""

from __future__ import annotations

import json
import os
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

from loopbloom.core.models import GoalArea
from loopbloom.storage.base import Storage, StorageError

DEFAULT_PATH = Path(
    os.getenv("LOOPBLOOM_SQLITE_PATH", Path.home() / ".loopbloom" / "data.db")
)
DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)

metadata = MetaData()

raw_table = Table(
    "raw_json",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("payload", String, nullable=False),
)


class SQLiteStore(Storage):
    """Store goals in a single-row SQLite table."""

    def __init__(self, path: Path | str = DEFAULT_PATH):
        """Initialise the SQLite store."""
        self._engine: Engine = create_engine(f"sqlite:///{path}", future=True)
        metadata.create_all(self._engine)

    def load(self) -> List[GoalArea]:
        """Return stored GoalAreas from disk."""
        try:
            with self._engine.begin() as conn:
                rows = conn.execute(select(raw_table.c.payload)).scalars().all()
            if not rows:
                return []
            # assume single row
            data = json.loads(rows[0])
            return [GoalArea.model_validate(obj) for obj in data]
        except SQLAlchemyError as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc

    def save(self, goals: List[GoalArea]) -> None:
        """Persist GoalAreas atomically."""
        payload = json.dumps([g.model_dump(mode="json") for g in goals])
        try:
            with self._engine.begin() as conn:
                conn.execute(delete(raw_table))
                conn.execute(insert(raw_table).values(payload=payload))
        except SQLAlchemyError as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc
