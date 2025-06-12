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


def test_cope_run_invalid(tmp_path):
    """Running a nonexistent coping plan yields an error message."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    res = runner.invoke(cli, ["cope", "run", "nope"], env=env)
    assert "Plan not found" in res.output
