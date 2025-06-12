"""Integration tests for export and config commands."""

import csv
import json

from click.testing import CliRunner


def test_config_set_get_view(tmp_path):
    """Ensure config get/set/view round-trips values."""
    runner = CliRunner()
    import loopbloom.__main__ as main

    res = runner.invoke(main.cli, ["config", "set", "notify", "desktop"])
    assert "Saved" in res.output
    res = runner.invoke(main.cli, ["config", "get", "notify"])
    assert "desktop" in res.output
    res = runner.invoke(main.cli, ["config", "view"])
    assert "notify" in res.output


def test_export_json_and_csv(tmp_path):
    """Export data in both JSON and CSV formats."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    import importlib
    import os

    import loopbloom.__main__ as main
    import loopbloom.cli as cli_mod
    import loopbloom.cli.export as export_mod
    import loopbloom.storage.json_store as js_mod

    os.environ["LOOPBLOOM_DATA_PATH"] = str(tmp_path / "data.json")
    importlib.reload(js_mod)
    importlib.reload(cli_mod)
    importlib.reload(export_mod)
    importlib.reload(main)

    runner.invoke(main.cli, ["goal", "add", "Sleep"], env=env)
    runner.invoke(main.cli, ["goal", "phase", "add", "Sleep", "Base"], env=env)
    runner.invoke(
        main.cli,
        ["goal", "micro", "add", "Wake 8", "--goal", "Sleep", "--phase", "Base"],
        env=env,
    )
    runner.invoke(main.cli, ["checkin", "Sleep"], env=env)

    json_path = tmp_path / "export.json"
    csv_path = tmp_path / "export.csv"
    runner.invoke(
        main.cli,
        ["export", "--fmt", "json", "--out", str(json_path)],
        env=env,
    )
    runner.invoke(
        main.cli,
        ["export", "--fmt", "csv", "--out", str(csv_path)],
        env=env,
    )
    data = json.loads(json_path.read_text())
    assert data and data[0]["name"] == "Sleep"
    assert sum(1 for _ in csv.reader(csv_path.open())) == 2
