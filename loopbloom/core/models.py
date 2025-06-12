"""Pydantic data models for Loop Bloom."""

from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class Status(str, Enum):
    """Lifecycle of a MicroGoal."""

    active = "active"
    cancelled = "cancelled"
    complete = "complete"


class Checkin(BaseModel):
    """A single daily micro-goal check-in."""

    date: dt_date = Field(default_factory=dt_date.today)
    success: bool
    note: str | None = None
    self_talk_generated: str | None = None


class MicroGoal(BaseModel):
    """A very small behavioural target the user wants to track."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: Status = Status.active
    created_at: datetime = Field(default_factory=datetime.utcnow)
    checkins: list[Checkin] = Field(default_factory=list)

    @field_validator("name")
    def _strip(cls, v: str) -> str:  # noqa: D401
        return v.strip()


class Phase(BaseModel):
    """A collection of micro-goals grouped under a named phase."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    micro_goals: list[MicroGoal] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GoalArea(BaseModel):
    """Top-level goal area containing multiple phases."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phases: list[Phase] = Field(default_factory=list)
    micro_goals: list[MicroGoal] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
