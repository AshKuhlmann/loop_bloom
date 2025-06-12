import importlib
import pytest
from click.testing import CliRunner


# Helper function to reload modules for test isolation
def reload_modules():
    """Reloads the core application modules to ensure a clean state."""
    # It's important to reload modules in the correct order of dependency
    import loopbloom.storage.json_store as js_mod
    import loopbloom.core.config as config_mod
    import loopbloom.cli as cli_mod
    import loopbloom.cli.goal as goal_mod
    import loopbloom.cli.checkin as checkin_mod
    import loopbloom.cli.summary as summary_mod
    import loopbloom.cli.cope as cope_mod
    import loopbloom.cli.export as export_mod
    from loopbloom import __main__ as main

    importlib.reload(js_mod)
    importlib.reload(config_mod)
    importlib.reload(cli_mod)
    importlib.reload(goal_mod)
    importlib.reload(checkin_mod)
    importlib.reload(summary_mod)
    importlib.reload(cope_mod)
    importlib.reload(export_mod)
    importlib.reload(main)
    return main.cli


@pytest.fixture(scope="function")
def runner():
    """Provides a CliRunner instance for invoking CLI commands."""
    return CliRunner()


@pytest.fixture(scope="function")
def isolated_env(tmp_path, monkeypatch):
    """
    Creates an isolated environment for each test function.
    - Sets up a temporary data directory.
    - Sets environment variables to point to this directory.
    - Ensures modules are reloaded to use the new paths.
    """
    data_path = tmp_path / "data.json"
    config_path = tmp_path / "config.toml"

    # Use monkeypatch to set environment variables for the duration of the test
    monkeypatch.setenv("LOOPBLOOM_DATA_PATH", str(data_path))
    monkeypatch.setenv("LOOPBLOOM_CONFIG_PATH", str(config_path))

    # Ensure the CLI uses the patched environment
    cli = reload_modules()

    return {
        "runner": CliRunner(),
        "cli": cli,
        "data_path": data_path,
        "config_path": config_path,
        "env": {
            "LOOPBLOOM_DATA_PATH": str(data_path),
            "LOOPBLOOM_CONFIG_PATH": str(config_path),
        }
    }
