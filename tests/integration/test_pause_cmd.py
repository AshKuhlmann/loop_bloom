import importlib

from click.testing import CliRunner

import loopbloom.core.config as cfg_mod


class TestPauseCommand:
    def test_pause_with_invalid_duration_format(self, tmp_path, monkeypatch):
        """Invalid duration strings should not alter the config."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        importlib.reload(cfg_mod)
        import loopbloom.__main__ as main

        importlib.reload(main)

        runner = CliRunner()
        env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

        runner.invoke(main.cli, ["goal", "add", "Test Goal"], env=env)
        result = runner.invoke(main.cli, ["pause", "--for", "2months"], env=env)

        assert result.exit_code != 0
        assert "Invalid duration format" in result.output

        conf = cfg_mod.load()
        assert conf.get("pause_until", "") == ""
        assert conf.get("goal_pauses", {}) == {}

    def test_pause_goal_with_invalid_duration(self, tmp_path, monkeypatch):
        """Pausing a specific goal with an invalid duration fails gracefully."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        importlib.reload(cfg_mod)
        import loopbloom.__main__ as main

        importlib.reload(main)

        runner = CliRunner()
        env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}

        runner.invoke(main.cli, ["goal", "add", "Another Goal"], env=env)
        result = runner.invoke(
            main.cli,
            ["pause", "--goal", "Another Goal", "--for", "1year"],
            env=env,
        )

        assert result.exit_code != 0
        assert "Invalid duration format" in result.output

        conf = cfg_mod.load()
        assert "Another Goal" not in conf.get("goal_pauses", {})


def test_pause_global(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    import loopbloom.__main__ as main

    importlib.reload(main)
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    runner.invoke(main.cli, ["goal", "add", "G"], env=env)
    runner.invoke(main.cli, ["micro", "add", "M", "--goal", "G"], env=env)
    runner.invoke(main.cli, ["pause", "--for", "1d"], env=env)
    runner.invoke(main.cli, ["config", "set", "notify", "desktop"], env=env)
    calls: list[str] = []

    def fake_notify(title, message, timeout):
        calls.append(message)

    monkeypatch.setattr(
        "loopbloom.services.notifier.notification",
        type("X", (), {"notify": fake_notify}),
    )
    runner.invoke(main.cli, ["checkin", "G"], env=env)
    assert not calls


def test_pause_specific_goal(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import loopbloom.core.config as cfg_mod

    importlib.reload(cfg_mod)
    import loopbloom.__main__ as main

    importlib.reload(main)
    runner = CliRunner()
    env = {"LOOPBLOOM_DATA_PATH": str(tmp_path / "data.json")}
    runner.invoke(main.cli, ["goal", "add", "A"], env=env)
    runner.invoke(main.cli, ["goal", "add", "B"], env=env)
    runner.invoke(main.cli, ["micro", "add", "M", "--goal", "A"], env=env)
    runner.invoke(main.cli, ["micro", "add", "N", "--goal", "B"], env=env)
    runner.invoke(main.cli, ["pause", "--goal", "A", "--for", "1d"], env=env)
    runner.invoke(main.cli, ["config", "set", "notify", "desktop"], env=env)
    calls: list[str] = []

    def fake_notify(title, message, timeout):
        calls.append(message)

    monkeypatch.setattr(
        "loopbloom.services.notifier.notification",
        type("X", (), {"notify": fake_notify}),
    )
    runner.invoke(main.cli, ["checkin", "A"], env=env)
    assert len(calls) == 0
    runner.invoke(main.cli, ["checkin", "B"], env=env)
    assert len(calls) == 1
