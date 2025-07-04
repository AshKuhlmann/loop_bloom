from click.testing import CliRunner

from loopbloom.__main__ import cli


def test_running_coping_plan(tmp_path) -> None:
    """Test Case 4.2: Running a Coping Plan."""
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

    # Provide answers for the two prompts in the built-in plan.
    user_input = "\n".join(["inbox backlog", "sort emails"]) + "\n"
    result = runner.invoke(
        cli,
        ["cope", "run", "overwhelmed"],
        env=env,
        input=user_input,
    )

    assert result.exit_code == 0
    assert "Feeling Overwhelmed" in result.output
    assert "Identify the biggest stressor" in result.output
    assert "Pick one micro-action" in result.output
    assert "Great job" in result.output
