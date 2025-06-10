"""YAML-driven coping-plan engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

COPING_DIR = Path(__file__).resolve().parent.parent / "data" / "coping"


class CopingPlanError(RuntimeError):
    """Raised for invalid coping plan definitions."""


class Step:
    """Single interaction step within a coping plan."""

    def __init__(self, raw: Dict[str, Any]):
        """Initialize from a raw dictionary."""
        self.prompt = raw.get("prompt")
        self.message = raw.get("message")
        self.store_as = raw.get("store_as")
        if not (self.prompt or self.message):
            raise CopingPlanError("Step must have prompt or message")


class CopingPlan:
    """Parsed coping plan from YAML."""

    def __init__(self, path: Path):
        """Load plan from ``path``."""
        content = yaml.safe_load(path.read_text())
        self.id = content["id"]
        self.title = content["title"]
        self.steps = [Step(s) for s in content["steps"]]


class PlanRepository:
    """Access coping plans stored on disk."""

    @staticmethod
    def list_plans() -> List[CopingPlan]:
        """Return all available plans."""
        return [CopingPlan(p) for p in COPING_DIR.glob("*.yml")]

    @staticmethod
    def get(plan_id: str) -> CopingPlan | None:
        """Return plan matching ``plan_id`` or ``None``."""
        for p in COPING_DIR.glob("*.yml"):
            if p.stem == plan_id:
                return CopingPlan(p)
        return None


def run_plan(plan: CopingPlan) -> None:
    """Interactively walk through ``plan`` via standard input/output."""
    ctx: Dict[str, str] = {}
    for s in plan.steps:
        if s.prompt:
            answer = input(f"👉 {s.prompt} ")
            if s.store_as:
                ctx[s.store_as] = answer
        elif s.message:
            print(s.message.format(**ctx))
