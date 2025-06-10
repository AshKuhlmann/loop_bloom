"""Integration tests for the `cope` CLI command."""

from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_cope_list_and_run(tmp_path, monkeypatch):
    """List plans then run the sample one."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    res = runner.invoke(cli, ["cope", "list"], env=env)
    assert "overwhelmed" in res.output

    monkeypatch.setattr("builtins.input", lambda _: "inbox backlog")
    res = runner.invoke(cli, ["cope", "run", "overwhelmed"], env=env)
    assert "Great job" in res.output
