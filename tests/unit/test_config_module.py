"""Unit tests for config module."""

from loopbloom.core import config as cfg


def test_deep_merge() -> None:
    """_deep_merge combines nested dictionaries."""
    a = {"a": 1, "b": {"c": 2}}
    b = {"b": {"d": 3}}
    merged = cfg._deep_merge(a, b)
    assert merged["b"]["c"] == 2 and merged["b"]["d"] == 3
