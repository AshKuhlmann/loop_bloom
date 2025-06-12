"""Integration test for creating a new coping plan."""

import importlib

from click.testing import CliRunner


def test_cope_new(tmp_path, monkeypatch):
    """Interactively create a plan and verify the YAML output."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    coping_dir = tmp_path / "coping"
    coping_dir.mkdir()

    import loopbloom.core.coping as cp_mod

    monkeypatch.setattr(cp_mod, "COPING_DIR", coping_dir)
    import loopbloom.cli as cli_mod
    import loopbloom.cli.cope as cope_mod

    importlib.reload(cope_mod)
    importlib.reload(cli_mod)
    importlib.reload(cp_mod)
    import loopbloom.__main__ as main

    importlib.reload(main)
    new_cli = main.cli

    user_input = "\n".join(
        [
            "myplan",
            "My Plan",
            "p",
            "What is up?",
            "issue",
            "m",
            "Keep going!",
            "q",
        ]
    )

    res = runner.invoke(new_cli, ["cope", "new"], env=env, input=user_input)
    assert res.exit_code == 0
    created = coping_dir / "myplan.yml"
    assert created.exists()

    import yaml

    content = yaml.safe_load(created.read_text())
    assert content["id"] == "myplan"
    assert content["steps"][0]["prompt"] == "What is up?"
