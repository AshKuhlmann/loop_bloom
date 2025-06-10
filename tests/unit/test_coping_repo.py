"""Unit tests for coping plan repository."""

from loopbloom.core.coping import PlanRepository


def test_can_list_and_get_plans():
    """List plans then fetch one by ID."""
    plans = PlanRepository.list_plans()
    assert plans, "At least one plan expected"
    plan = PlanRepository.get(plans[0].id)
    assert plan.title == plans[0].title
