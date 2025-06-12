"""Interactive CLI helpers."""

from __future__ import annotations

from typing import Iterable, List, Optional, TypeVar

import click

T = TypeVar("T")


def choose_from(options: Iterable[T], prompt: str) -> Optional[T]:
    """Show numbered menu of ``options`` and return the chosen item."""
    items: List[T] = list(options)
    if not items:
        return None
    for i, opt in enumerate(items, 1):
        click.echo(f"{i}. {opt}")
    idx = click.prompt("Enter number", type=click.IntRange(1, len(items)))
    return items[idx - 1]
