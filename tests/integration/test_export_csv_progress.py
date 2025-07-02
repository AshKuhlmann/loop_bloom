import csv
from datetime import date

from click.testing import CliRunner

from loopbloom import __main__ as main


def test_export_to_csv(tmp_path):
    """Test Case 5.1: Export to CSV."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    runner.invoke(main.cli, ["goal", "add", "Exercise"], env=env)
    runner.invoke(main.cli, ["goal", "phase", "add", "Exercise", "Start"], env=env)
    runner.invoke(
        main.cli,
        ["micro", "add", "Walk", "--goal", "Exercise", "--phase", "Start"],
        env=env,
    )

    runner.invoke(main.cli, ["checkin", "Exercise"], env=env)
    runner.invoke(main.cli, ["checkin", "Exercise", "--skip"], env=env)

    csv_path = tmp_path / "progress.csv"
    res = runner.invoke(
        main.cli, ["export", "--fmt", "csv", "--out", str(csv_path)], env=env
    )

    assert res.exit_code == 0
    assert csv_path.exists()

    rows = list(csv.DictReader(csv_path.open()))
    assert len(rows) == 2
    today = str(date.today())
    assert rows[0]["date"] == today
    assert rows[0]["goal"] == "Exercise"
    assert rows[0]["phase"] == "Start"
    assert rows[0]["micro"] == "Walk"
    assert rows[0]["success"] == "1"
    assert rows[1]["success"] == "0"
