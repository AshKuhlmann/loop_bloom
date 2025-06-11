"""Tests for notifier service."""

from loopbloom.services import notifier


def test_terminal_notify_caps(monkeypatch, capsys):
    """Fallbacks to terminal when plyer missing."""
    monkeypatch.setattr("loopbloom.services.notifier.notification", None)
    notifier.send("Title", "Msg", mode="desktop")
    captured = capsys.readouterr()
    assert "Title" in captured.out
