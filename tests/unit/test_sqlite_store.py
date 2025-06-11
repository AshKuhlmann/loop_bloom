"""Tests for the SQLite storage backend."""

from pathlib import Path

from loopbloom.core.models import GoalArea
from loopbloom.storage.sqlite_store import SQLiteStore


def test_sqlite_roundtrip(tmp_path: Path):
    """Ensure data saved and loaded roundtrips correctly."""
    store = SQLiteStore(path=tmp_path / "data.db")
    goals = [GoalArea(name="SQLTest")]
    store.save(goals)
    loaded = store.load()
    assert loaded[0].name == "SQLTest"
