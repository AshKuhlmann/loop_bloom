"""Business logic wrapper for goal progression."""

from __future__ import annotations

from loopbloom.core.models import GoalArea
from loopbloom.core.progression import get_progression_reasons, should_advance


class ProgressionService:
    """Handles the business logic for goal progression."""

    @staticmethod
    def check_progression(goal: GoalArea) -> tuple[bool, list[str]]:
        """Return whether ``goal`` should advance to the next micro-habit."""
        micro = goal.get_active_micro_goal()
        if micro is None:
            return False, ["No active micro-goal."]
        should_progress = should_advance(micro)
        reasons = get_progression_reasons(micro)
        return should_progress, reasons
