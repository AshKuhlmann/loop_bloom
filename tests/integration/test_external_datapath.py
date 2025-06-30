import importlib
from click.testing import CliRunner


def test_cli_respects_config_data_path(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv("LOOPBLOOM_DATA_PATH", raising=False)
    monkeypatch.delenv("LOOPBLOOM_SQLITE_PATH", raising=False)
    import loopbloom.core.config as cfg_mod
    importlib.reload(cfg_mod)

    # Configure custom data path then reload the CLI to pick it up.
    data_file = tmp_path / "external.json"
    cfg_mod.save({"data_path": str(data_file)})

    from loopbloom import __main__ as main
    importlib.reload(main)

    runner = CliRunner()
    res = runner.invoke(main.cli, ["goal", "add", "Persist"], env={})
    assert res.exit_code == 0
    assert data_file.exists()
