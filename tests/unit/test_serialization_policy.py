from __future__ import annotations

import importlib
import json
from datetime import datetime
from pathlib import Path


def test_json_store_serializes_datetimes_as_iso_strings(tmp_path: Path) -> None:
    from loopbloom.core.models import GoalArea
    from loopbloom.storage.json_store import JSONStore

    p = tmp_path / "data.json"
    store = JSONStore(path=p)
    store.save([GoalArea(name="G")])

    raw = json.loads(p.read_text())
    assert isinstance(raw, list) and raw
    created_at = raw[0]["created_at"]
    assert isinstance(created_at, str) and "T" in created_at
    # Should be parseable as ISO 8601 by Python
    datetime.fromisoformat(created_at)


def _reload_review(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import loopbloom.constants as const_mod
    import loopbloom.core.review as review_mod

    importlib.reload(const_mod)
    importlib.reload(review_mod)
    return review_mod


def _reload_journal(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import loopbloom.constants as const_mod
    import loopbloom.core.journal as journal_mod

    importlib.reload(const_mod)
    importlib.reload(journal_mod)
    return journal_mod


def test_review_json_timestamp_is_iso(tmp_path: Path, monkeypatch) -> None:
    review_mod = _reload_review(tmp_path, monkeypatch)
    review_mod.add_entry("week", "Great work")
    data = json.loads(review_mod.REVIEW_PATH.read_text())
    assert isinstance(data[0]["timestamp"], str)
    datetime.fromisoformat(data[0]["timestamp"])  # parseable


def test_journal_json_timestamp_is_iso(tmp_path: Path, monkeypatch) -> None:
    journal_mod = _reload_journal(tmp_path, monkeypatch)
    journal_mod.add_entry("note", goal="G1")
    data = json.loads(journal_mod.JOURNAL_PATH.read_text())
    assert isinstance(data[0]["timestamp"], str)
    datetime.fromisoformat(data[0]["timestamp"])  # parseable
