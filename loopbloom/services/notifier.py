"""Cross-platform desktop notifications via plyer.

The :func:`send` helper abstracts away optional dependencies so the rest
of the codebase can request a notification without worrying about the
platform.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from loopbloom.core import config as cfg

try:
    from plyer import notification
except ImportError:  # pragma: no cover
    # ``plyer`` is optional; fall back to terminal notifications if missing.
    notification = None

NotifyMode = Literal["terminal", "desktop", "none"]


def send(
    title: str,
    message: str,
    *,
    mode: NotifyMode = "terminal",
    goal: str | None = None,
) -> None:  # noqa: D401
    """Deliver a notification to the user.

    Args:
        title: Title text for the notification.
        message: Body of the notification.
        mode: Delivery mechanism; ``terminal``, ``desktop`` or ``none``.
        goal: Optional goal name used when checking pause settings.

    Returns:
        None
    """
    # ``mode`` controls the delivery mechanism. ``desktop`` uses plyer,
    # ``terminal`` prints to stdout, and ``none`` disables notifications.
    config = cfg.load()
    pause_until = config.get("pause_until")
    if pause_until:
        try:
            if date.today() <= date.fromisoformat(pause_until):
                return
        except ValueError:
            pass
    if goal:
        gp = config.get("goal_pauses", {})
        until = gp.get(goal)
        if until:
            try:
                if date.today() <= date.fromisoformat(until):
                    return
            except ValueError:
                pass

    if mode == "none":
        return
    if mode == "desktop":
        if notification is None:
            print("[yellow]plyer not installed – falling back to terminal")
            mode = "terminal"
        else:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    timeout=5,
                )
                return
            except Exception:
                # pragma: no cover - plyer may fail without backend
                print("Desktop notify failed; falling back to terminal")
    # terminal fallback
    # Display a simple message when desktop notifications aren't available.
    print(f"\n🔔  {title}: {message}\n")
