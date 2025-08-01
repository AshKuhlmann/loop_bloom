"""Pydantic data models for Loop Bloom.

These classes define the goal → phase → micro-habit hierarchy and are
persisted via the storage backends.
"""

from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from loopbloom.services.datetime import get_current_datetime


class Status(str, Enum):
    """Lifecycle stages for a :class:`MicroGoal`."""

    active = "active"
    cancelled = "cancelled"
    complete = "complete"


class Checkin(BaseModel):
    """A single daily micro-goal check-in."""

    # Store the day separately from the timestamp so daily statistics remain
    # consistent regardless of timezone.
    date: dt_date = Field(default_factory=lambda: get_current_datetime().date())
    success: bool
    note: str | None = None
    # Persist the pep talk shown to the user so past encouragement can be
    # displayed alongside the check-in history.
    self_talk_generated: str | None = None


class MicroGoal(BaseModel):
    """A very small behavioural target the user wants to track."""

    # Use a UUID rather than the name so references remain valid even if the
    # micro-habit gets renamed later.
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: Status = Status.active
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Chronological log of successes and skips used when calculating streaks
    # and advancement eligibility.
    checkins: list[Checkin] = Field(default_factory=list)
    # Allow this micro-habit to override the global advancement rules with its
    # own window and threshold values.
    advancement_window: int | None = None
    advancement_threshold: float | None = None

    @field_validator("name")
    def _strip(cls, v: str) -> str:  # noqa: D401
        """Normalize whitespace around the name.

        Args:
            v: Raw name string potentially containing surrounding spaces.

        Returns:
            str: The cleaned name.
        """
        # Validators in Pydantic V2 must be class methods; we simply strip
        # leading/trailing whitespace when models are parsed or created.
        return v.strip()


class Phase(BaseModel):
    """A collection of micro-goals grouped under a named phase."""

    # Unique ID to allow stable references even if names change.
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    notes: str | None = None
    micro_goals: list[MicroGoal] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GoalArea(BaseModel):
    """Top-level goal area containing multiple phases."""

    # Unique ID for this goal area.
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    notes: str | None = None
    phases: list[Phase] = Field(default_factory=list)
    micro_goals: list[MicroGoal] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def get_active_micro_goal(self) -> MicroGoal | None:
        """Return the currently active micro-goal if one exists."""
        # Search phases first to match the user's hierarchical structure.
        for ph in self.phases:
            mg = next(
                (m for m in ph.micro_goals if m.status == Status.active),
                None,
            )
            if mg:
                return mg
        # Fall back to any active micro-goals attached directly to the goal
        # if none are active within phases.
        # ``None`` is returned if nothing is active anywhere.
        return next(
            (m for m in self.micro_goals if m.status == Status.active),
            None,
        )
