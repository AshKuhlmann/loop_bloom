"""Tests for the :mod:`loopbloom.storage.json_store` module."""

from pathlib import Path

from loopbloom.core.models import GoalArea
from loopbloom.storage.json_store import JSONStore


def test_json_store_roundtrip(tmp_path: Path) -> None:
    """Store a goal area then load it back from disk."""
    store = JSONStore(path=tmp_path / "data.json")
    goals = [GoalArea(name="Sleep Hygiene")]
    store.save(goals)
    loaded = store.load()
    assert loaded[0].name == "Sleep Hygiene"
