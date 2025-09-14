from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner


def test_all_top_level_commands_have_help(monkeypatch) -> None:
    """Every registered top-level command should provide --help successfully.

    This ensures new commands are at least minimally documented and wired up.
    """
    from loopbloom import __main__ as main

    # Isolate any filesystem writes under a temp path
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(Path.cwd() / ".tmp-x" / "data.json"))

    runner = CliRunner()
    # Ensure commands are registered
    commands = dict(main.cli.commands)
    assert commands, "No commands registered on CLI"

    for name in commands.keys():
        res = runner.invoke(
            main.cli, [name, "--help"]
        )  # groups and commands both support --help
        assert res.exit_code == 0, f"--help failed for command: {name}"
