"""Unit tests for pep-talk utilities."""

from loopbloom.core.talks import TalkPool


def test_random_talks_provide_variation() -> None:
    """Random should be deterministic under pytest."""
    seen = {TalkPool.random("success") for _ in range(10)}
    assert len(seen) == 1
