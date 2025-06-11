"""Cross-platform desktop notifications via plyer."""

from __future__ import annotations

from typing import Literal

try:
    from plyer import notification
except ImportError:  # pragma: no cover
    notification = None

NotifyMode = Literal["terminal", "desktop", "none"]


def send(
    title: str, message: str, *, mode: NotifyMode = "terminal"
) -> None:  # noqa: D401
    """Send a desktop or terminal notification."""
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
    print(f"\n🔔  {title}: {message}\n")
