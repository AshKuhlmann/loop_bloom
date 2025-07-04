import importlib

from click.testing import CliRunner


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
