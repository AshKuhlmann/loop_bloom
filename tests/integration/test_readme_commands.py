"""Tests for README command examples."""

import importlib

from click.testing import CliRunner


def test_readme_commands(tmp_path, monkeypatch):
    """Ensure README examples execute without error."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # isolate config and sqlite paths
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setenv("LOOPBLOOM_SQLITE_PATH", str(tmp_path / "db.sqlite"))

    import loopbloom.__main__ as main
    import loopbloom.cli as cli_mod
    import loopbloom.cli.checkin as checkin_mod
    import loopbloom.cli.config as config_mod
    import loopbloom.cli.cope as cope_mod
    import loopbloom.cli.export as export_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.cli.summary as summary_mod
    import loopbloom.cli.tree as tree_mod
    import loopbloom.core.config as cfg_mod

    # reload modules to apply env vars
    for mod in (
        cfg_mod,
        cli_mod,
        goal_mod,
        checkin_mod,
        summary_mod,
        cope_mod,
        config_mod,
        export_mod,
        tree_mod,
        main,
    ):
        importlib.reload(mod)

    cli = main.cli

    # Quick Start commands
    assert runner.invoke(cli, ["goal", "add", "Sleep Hygiene"], env=env).exit_code == 0
    assert (
        runner.invoke(
            cli, ["goal", "phase", "add", "Sleep Hygiene", "Base"], env=env
        ).exit_code
        == 0
    )
    assert (
        runner.invoke(
            cli,
            ["goal", "micro", "add", "Sleep Hygiene", "Base", "Wake up at 08:00"],
            env=env,
        ).exit_code
        == 0
    )
    res = runner.invoke(
        cli,
        ["checkin", "Sleep Hygiene", "--success", "--note", "Groggy but did it!"],
        env=env,
    )
    assert res.exit_code == 0

    # Sample session snippets
    runner.invoke(cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(cli, ["goal", "phase", "add", "Exercise", "Foundation"], env=env)
    runner.invoke(
        cli, ["goal", "micro", "add", "Exercise", "Foundation", "Walk 5 min"], env=env
    )
    assert "LoopBloom" in runner.invoke(cli, ["summary"], env=env).output
    assert (
        "Exercise"
        in runner.invoke(cli, ["summary", "--goal", "Exercise"], env=env).output
    )
    assert (
        runner.invoke(
            cli,
            ["checkin", "Exercise", "--skip", "--note", "Rainy"],
            env=env,
        ).exit_code
        == 0
    )
    assert (
        "Great"
        in runner.invoke(
            cli,
            ["cope", "run", "overwhelmed"],
            input="inbox backlog\ntriage 5 emails\n",
            env=env,
        ).output
    )

    # Cheatsheet/Config/Data Export
    assert "overwhelmed" in runner.invoke(cli, ["cope", "list"]).output
    assert "Saved" in runner.invoke(cli, ["config", "set", "storage", "sqlite"]).output
    assert "Saved" in runner.invoke(cli, ["config", "set", "notify", "desktop"]).output
    cfg_out = runner.invoke(cli, ["config", "view"]).output
    assert "notify" in cfg_out
    csv_path = tmp_path / "progress.csv"
    assert (
        runner.invoke(
            cli, ["export", "--fmt", "csv", "--out", str(csv_path)], env=env
        ).exit_code
        == 0
    )
    assert csv_path.exists()
    tree_out = runner.invoke(cli, ["tree"], env=env).output
    assert "Sleep Hygiene" in tree_out and "Exercise" in tree_out
    help_out = runner.invoke(cli, ["--help"]).output
    assert "Commands" in help_out
