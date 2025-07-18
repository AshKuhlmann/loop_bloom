"""Tests for the Pydantic data models."""

from datetime import date, timedelta

from loopbloom.core.models import Checkin, GoalArea, MicroGoal, Phase, Status


def test_goal_hierarchy_roundtrip() -> None:
    """Ensure nested models survive a dump/load cycle."""
    mg = MicroGoal(name="Walk 5 min")
    ph = Phase(name="Foundation", micro_goals=[mg])
    ga = GoalArea(name="Exercise", phases=[ph])
    dumped = ga.model_dump()
    reloaded = GoalArea.model_validate(dumped)
    assert reloaded.phases[0].micro_goals[0].name == "Walk 5 min"


def test_checkin_success_ratio() -> None:
    """Quick sanity check on check-in accumulation."""
    mg = MicroGoal(name="Test")
    mg.checkins.extend(
        [
            Checkin(
                date=date.today() - timedelta(days=i),
                success=True,
            )
            for i in range(5)
        ]
    )
    assert len(mg.checkins) == 5


def test_status_enum() -> None:
    """Enum members expose the correct value."""
    assert Status.active.value == "active"


def test_microgoal_name_trimmed() -> None:
    """Whitespace is stripped from names."""
    mg = MicroGoal(name="  Walk  ")
    assert mg.name == "Walk"


def test_goalarea_get_active_micro_goal() -> None:
    """Return the active micro-goal from phases or direct list."""
    active = MicroGoal(name="Active")
    phase = Phase(
        name="P",
        micro_goals=[MicroGoal(name="Done", status=Status.complete), active],
    )
    ga = GoalArea(
        name="G",
        phases=[phase],
        micro_goals=[MicroGoal(name="Direct", status=Status.complete)],
    )
    assert ga.get_active_micro_goal() is active

    # No active in phases; fall back to direct micro-goals
    for mg in phase.micro_goals:
        mg.status = Status.complete
    direct_active = MicroGoal(name="Direct Active")
    ga.micro_goals.append(direct_active)
    assert ga.get_active_micro_goal() is direct_active
