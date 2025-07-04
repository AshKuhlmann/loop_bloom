from __future__ import annotations

import importlib
import json
from pathlib import Path

from click.testing import CliRunner


def _reload_cli(tmp_path: Path, monkeypatch) -> any:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import loopbloom.__main__ as main
    import loopbloom.core.config as cfg_mod
    import loopbloom.core.journal as journal_mod

    importlib.reload(cfg_mod)
    importlib.reload(journal_mod)
    importlib.reload(main)
    return main.cli


def test_journal_creates_entry(tmp_path: Path, monkeypatch) -> None:
    cli = _reload_cli(tmp_path, monkeypatch)
    runner = CliRunner()
    res = runner.invoke(
        cli,
        ["journal", "test entry", "--goal", "Sleep"],
        env={},
    )
    assert "Entry saved" in res.output
    journal_file = Path(tmp_path) / "loopbloom" / "journal.json"
    data = json.loads(journal_file.read_text())
    assert data[0]["text"] == "test entry"
    assert data[0]["goal"] == "Sleep"
