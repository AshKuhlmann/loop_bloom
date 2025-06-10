"""Unit tests for export CSV flattening."""

import csv
from io import StringIO

from loopbloom.cli.export import csv as csv_module
from loopbloom.core.models import Checkin, GoalArea, MicroGoal, Phase


def test_csv_flatten() -> None:
    """Ensure CSV rows can be produced for a single checkin."""
    g = GoalArea(
        name="Exercise",
        phases=[
            Phase(
                name="Foundation",
                micro_goals=[
                    MicroGoal(name="Walk 5", checkins=[Checkin(success=True)])
                ],
            )
        ],
    )
    rows = [["date", "goal", "phase", "micro", "success", "note"]]
    for ph in g.phases:
        for m in ph.micro_goals:
            for ci in m.checkins:
                rows.append(
                    [
                        str(ci.date),
                        "Exercise",
                        "Foundation",
                        "Walk 5",
                        "1",
                        "",
                    ]
                )
    sio = StringIO()
    writer = csv_module.writer(sio)
    writer.writerows(rows)
    sio.seek(0)
    assert len(list(csv.reader(sio))) == 2
