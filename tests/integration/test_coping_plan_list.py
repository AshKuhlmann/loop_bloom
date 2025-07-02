from click.testing import CliRunner
from loopbloom.__main__ import cli


def test_accessing_coping_plans(tmp_path):
    """Test Case 4.1: Accessing Coping Plans."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    result = runner.invoke(cli, ["cope", "list"], env=env)
    assert result.exit_code == 0
    assert "overwhelmed" in result.output
