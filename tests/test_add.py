"""Tests for the example ``add`` function."""

from loop_bloom import add


def test_add() -> None:
    """``add`` simply adds two integers."""
    assert add(1, 2) == 3
