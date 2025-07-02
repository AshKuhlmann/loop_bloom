from __future__ import annotations

import importlib
import json
from pathlib import Path

from click.testing import CliRunner


def _reload_cli(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import loopbloom.core.config as cfg_mod
    import loopbloom.core.review as review_mod
    import loopbloom.__main__ as main
    importlib.reload(cfg_mod)
    importlib.reload(review_mod)
    importlib.reload(main)
    return main.cli


def test_review_creates_entry(tmp_path: Path, monkeypatch) -> None:
    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    res = runner.invoke(
        cli,
        ["review", "--period", "week"],
        input="Great progress\n",
    )
    assert "Review saved" in res.output
    review_file = Path(tmp_path) / "loopbloom" / "reviews.json"
    data = json.loads(review_file.read_text())
    assert data[0]["period"] == "week"
    assert data[0]["went_well"] == "Great progress"
