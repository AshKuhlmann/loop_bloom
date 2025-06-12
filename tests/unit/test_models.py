from loopbloom.core.models import GoalArea, MicroGoal


def test_goal_with_direct_microgoal_roundtrip() -> None:
    """Ensure a goal with a direct micro-goal survives a dump/load cycle."""
    mg = MicroGoal(name="Read one page")
    ga = GoalArea(name="Reading", micro_goals=[mg])
    dumped = ga.model_dump()
    reloaded = GoalArea.model_validate(dumped)
    assert reloaded.micro_goals[0].name == "Read one page"
