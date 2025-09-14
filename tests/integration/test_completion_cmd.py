from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner


def test_completion_explicit_shells(monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom import __main__ as main

    runner = CliRunner()
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(Path.cwd() / ".tmp-x" / "data.json"))

    cases = (
        ("bash", "_LOOPBLOOM_COMPLETE=bash_source", "loopbloom"),
        ("zsh", "_LOOPBLOOM_COMPLETE=zsh_source", "loopbloom"),
        ("fish", "env _LOOPBLOOM_COMPLETE=fish_source loopbloom", None),
        ("pwsh", "$Env:_LOOPBLOOM_COMPLETE = 'powershell'", None),
    )
    for shell, must_contain, also_contain in cases:
        res = runner.invoke(main.cli, ["completion", shell])
        assert res.exit_code == 0
        assert must_contain in res.output
        if also_contain:
            assert also_contain in res.output


def test_completion_detects_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    from loopbloom import __main__ as main

    runner = CliRunner()
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(Path.cwd() / ".tmp-x" / "data.json"))
    monkeypatch.setenv("SHELL", "/bin/zsh")

    res = runner.invoke(main.cli, ["completion"])  # detect from SHELL
    assert res.exit_code == 0
    assert "_LOOPBLOOM_COMPLETE=zsh_source" in res.output
