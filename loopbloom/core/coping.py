"""YAML-driven coping-plan engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

# Directory containing YAML coping plans bundled with the package.
COPING_DIR = Path(__file__).resolve().parent.parent / "data" / "coping"


class CopingPlanError(RuntimeError):
    """Raised for invalid coping plan definitions."""


class Step:
    """Single interaction step within a coping plan."""

    def __init__(self, raw: Dict[str, Any]):
        """Initialize from a raw dictionary."""
        # ``prompt`` means the plan expects user input at this step.
        self.prompt = raw.get("prompt")
        # ``message`` is printed verbatim, optionally using stored values.
        self.message = raw.get("message")
        # ``store_as`` names the variable to capture prompt answers under. It
        # can later be referenced as ``{store_as}`` in subsequent messages.
        self.store_as = raw.get("store_as")
        if not (self.prompt or self.message):
            raise CopingPlanError("Step must have prompt or message")


class CopingPlan:
    """Parsed coping plan from YAML."""

    def __init__(self, path: Path):
        """Load plan metadata and steps from a YAML file."""
        content = yaml.safe_load(path.read_text())
        self.id = content["id"]
        self.title = content["title"]
        self.steps = [Step(s) for s in content["steps"]]


class PlanRepository:
    """Access coping plans stored on disk."""

    @staticmethod
    def list_plans() -> List[CopingPlan]:
        """Return all available plans found in :data:`COPING_DIR`."""
        return [CopingPlan(p) for p in COPING_DIR.glob("*.yml")]

    @staticmethod
    def get(plan_id: str) -> CopingPlan | None:
        """Return plan matching ``plan_id`` or ``None`` if not found."""
        for p in COPING_DIR.glob("*.yml"):
            if p.stem == plan_id:
                return CopingPlan(p)
        return None


def run_plan(plan: CopingPlan) -> None:
    """Interactively walk through ``plan`` via standard input/output."""
    # Collected answers referenced by later steps. Step ``message`` templates
    # use ``str.format`` with this dictionary to inject previous responses.
    ctx: Dict[str, str] = {}
    for s in plan.steps:
        if s.prompt:
            answer = input(f"👉 {s.prompt} ")
            if s.store_as:
                ctx[s.store_as] = answer
        elif s.message:
            print(s.message.format(**ctx))
