"""Unit tests for pep-talk utilities."""

from loopbloom.core.talks import TalkPool


def test_random_talks_provide_variation() -> None:
    """Ensure random() returns varied results."""
    seen = {TalkPool.random("success") for _ in range(10)}
    assert len(seen) >= 2  # Variation expected
