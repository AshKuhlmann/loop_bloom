"""Interactive CLI helpers used across multiple commands."""

from __future__ import annotations

from typing import Iterable, List, Mapping, Optional, TypeVar

import click

# Generic type variable used by :func:`choose_from`.
T = TypeVar("T")


def choose_from(options: Iterable[T], prompt: str) -> Optional[T]:
    """Show a numbered menu of ``options`` and return the user's choice.

    Args:
        options: Sequence of selectable values.
        prompt: Prompt displayed when asking for the selection.

    Returns:
        The selected item or ``None`` if ``options`` is empty.
    """
    # Convert to a list so we can index user selections.
    items: List[T] = list(options)
    if not items:
        return None
    for i, opt in enumerate(items, 1):
        click.echo(f"{i}. {opt}")
    # Use ``click.IntRange`` to validate the choice automatically.
    idx: int = click.prompt(prompt, type=click.IntRange(1, len(items)))
    return items[idx - 1]


def interactive_select(prompt: str, options: Mapping[str, T]) -> Optional[T]:
    """Present a dictionary of options and return the chosen value.

    Args:
        prompt: Prompt displayed for selection.
        options: Mapping of label to value.

    Returns:
        The value corresponding to the selected label, or ``None`` when no
        options are provided.
    """
    if not options:
        return None
    labels = list(options.keys())
    for i, label in enumerate(labels, 1):
        click.echo(f"{i}. {label}")
    idx: int = click.prompt(prompt, type=click.IntRange(1, len(labels)))
    return options[labels[idx - 1]]
