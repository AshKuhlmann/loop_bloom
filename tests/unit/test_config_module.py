"""Unit tests for config module."""

from click.testing import CliRunner

from loopbloom.core import config as cfg


def test_deep_merge() -> None:
    """_deep_merge combines nested dictionaries."""
    a = {"a": 1, "b": {"c": 2}}
    b = {"b": {"d": 3}}
    merged = cfg._deep_merge(a, b)
    assert merged["b"]["c"] == 2 and merged["b"]["d"] == 3


def test_cli_set_casts_integer(tmp_path, monkeypatch) -> None:
    """Setting a numeric value results in an int in the config."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    import importlib

    import loopbloom.cli.config as cli_cfg
    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    importlib.reload(cli_cfg)

    runner = CliRunner()
    result = runner.invoke(cli_cfg._set, ["advance.window", "20"])
    assert "Saved." in result.output
    assert cfg_mod.load()["advance"]["window"] == 20


def test_cli_set_casts_boolean(tmp_path, monkeypatch) -> None:
    """Setting a boolean string stores ``True`` in the config."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    import importlib

    import loopbloom.cli.config as cli_cfg
    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    importlib.reload(cli_cfg)

    runner = CliRunner()
    result = runner.invoke(cli_cfg._set, ["notify", "true"])
    assert "Saved." in result.output
    assert cfg_mod.load()["notify"] is True


def test_cli_get_missing_key(tmp_path, monkeypatch) -> None:
    """Getting an unknown key shows an error message."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    import importlib

    import loopbloom.cli.config as cli_cfg
    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    importlib.reload(cli_cfg)

    runner = CliRunner()
    result = runner.invoke(cli_cfg._get, ["nonexistent.key"])
    assert "Key not found." in result.output
