# MicroHabits CLI – **Phase 0 & Phase 1 Implementation Playbook**

These instructions are designed for an autonomous coding agent (or junior developer) to go **from an empty project folder** to a fully-passing test suite for Phase 0 and Phase 1. Follow steps **in order**; do **not** deviate unless explicitly told.

---

## 🗂 Folder & File Overview (after Phase 1)

```
microhabits/
├── cli/                # empty for now (Phase 2)
├── core/
│   └── models.py       # Pydantic data models
├── storage/
│   ├── base.py         # Storage protocol
│   └── json_store.py   # JSON implementation
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   └── test_json_store.py
│   └── __init__.py
├── __init__.py
└── __main__.py
pyproject.toml
```

---

## Phase 0 — Project Scaffold  *(~20 min)*

> Goal: create a runnable package skeleton + tooling. No domain logic yet.

### 0‑1  Initialise Poetry & Git

1. `poetry new microhabits && cd microhabits`
2. Inside repo root, run:

```bash
poetry add pydantic click typer --group dev
poetry add pytest pytest-cov ruff black mypy beartype --group dev
```

3. Create a bare Git repo (`git init`) and commit the default poetry layout.

### 0‑2  Edit **`pyproject.toml`**

Add the following sections (or merge if present):

```toml
[tool.poetry]
name = "microhabits-cli"
version = "0.0.0"
description = "Compassion‑first micro‑habit tracker for the terminal."
packages = [{ include = "microhabits" }]

[tool.poetry.scripts]
micro = "microhabits.__main__:cli"

[tool.black]
line-length = 88

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "B", "W", "D"]

[tool.mypy]
strict = true
packages = "microhabits"

[build-system]
requires = ["poetry-core>=1.1.0"]
build-backend = "poetry.core.masonry.api"
```

### 0‑3  Add **`microhabits/__init__.py`**

```python
"""MicroHabits CLI package."""
__all__: list[str] = []
```

### 0‑4  Add **`microhabits/__main__.py`**

```python
"""Entry‑point stub – will be expanded in Phase 2."""
import click

@click.group(help="MicroHabits CLI – Phase 0 stub")
def cli() -> None:  # noqa: D401
    """Root command group."""


if __name__ == "__main__":  # pragma: no cover
    cli()
```

### 0‑5  Pre‑commit & Linters

1. `pre-commit sample-config > .pre-commit-config.yaml` (or copy below):

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks: [id: black]
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks: [id: ruff]
```

2. `pre-commit install`

### 0‑6  Smoke‑Test Script

Add **`tests/unit/test_smoke.py`**:

```python
def test_cli_help() -> None:
    import subprocess, sys

    result = subprocess.run(
        [sys.executable, "-m", "microhabits", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
```

### 0‑7  Commit & Verify

```bash
pytest -q
ruff .
black --check .
mypy microhabits  # will pass (empty stubs)
```

Commit results – **Phase 0 complete when all commands succeed.**

---

## Phase 1 — Data Models & JSON Persistence  *(~60 min)*

> Goal: implement domain models with Pydantic and a JSON storage adapter plus full unit tests (≥90 % cov).

### 1‑1  Create **`microhabits/core/models.py`**

```python
"""Pydantic data models for MicroHabits."""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class Status(str, Enum):
    """Lifecycle of a MicroGoal."""

    active = "active"
    cancelled = "cancelled"
    complete = "complete"


class Checkin(BaseModel):
    date: date = Field(default_factory=date.today)
    success: bool
    note: Optional[str] = None
    self_talk_generated: Optional[str] = None


class MicroGoal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    status: Status = Status.active
    created_at: datetime = Field(default_factory=datetime.utcnow)
    checkins: List[Checkin] = Field(default_factory=list)

    @validator("name")
    @classmethod
    def _strip(cls, v: str) -> str:  # noqa: D401
        return v.strip()


class Phase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    micro_goals: List[MicroGoal] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GoalArea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    phases: List[Phase] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 1‑2  Create **`microhabits/storage/base.py`**

```python
"""Storage abstraction.

CLI, services, and core modules depend *only* on this protocol, never on concrete IO.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import ContextManager, List, Protocol

from microhabits.core.models import GoalArea


class StorageError(RuntimeError):
    """Raised on IO failures."""


class Storage(Protocol):
    """Persistence interface."""

    def load(self) -> List[GoalArea]:
        """Return all goal areas from disk (or remote).

        Implementations must raise ``StorageError`` on unrecoverable errors and return
        ``[]`` on first-run / no-file conditions.
        """

    def save(self, goals: List[GoalArea]) -> None:  # noqa: D401
        """Persist full graph atomically."""

    @contextmanager  # type: ignore[arg-type]
    def lock(self) -> ContextManager[None]:  # noqa: D401
        """Optional advisory lock (no-op by default)."""
        yield
```

### 1‑3  Create **`microhabits/storage/json_store.py`**

```python
"""JSON-file implementation of Storage."""
from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

from pydantic.json import pydantic_encoder

from microhabits.core.models import GoalArea
from microhabits.storage.base import Storage, StorageError

DEFAULT_PATH = Path.home() / ".microhabits" / "data.json"
DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)


class JSONStore(Storage):
    """Atomic JSON persistence."""

    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:  # noqa: D401
        self._path = Path(path)

    def load(self) -> List[GoalArea]:  # noqa: D401
        if not self._path.exists():
            return []
        try:
            with self._path.open("r", encoding="utf-8") as fp:
                raw = json.load(fp)
            return [GoalArea.model_validate(obj) for obj in raw]
        except Exception as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc

    def save(self, goals: List[GoalArea]) -> None:  # noqa: D401
        tmp_path: Path
        try:
            with NamedTemporaryFile("w", delete=False, dir=self._path.parent) as tmp:
                json.dump(goals, tmp, default=pydantic_encoder, indent=2)
                tmp_path = Path(tmp.name)
            tmp_path.replace(self._path)
        except Exception as exc:  # pragma: no cover
            raise StorageError(str(exc)) from exc

    # Advisory lock not required for single-process Phase 1
    def lock(self):  # type: ignore[override]
        from contextlib import nullcontext

        return nullcontext()
```

### 1‑4  Unit Tests

#### `tests/unit/test_models.py`

```python
from datetime import date, timedelta

from microhabits.core.models import Checkin, GoalArea, MicroGoal, Phase, Status


def test_goal_hierarchy_roundtrip() -> None:
    mg = MicroGoal(name="Walk 5 min")
    ph = Phase(name="Foundation", micro_goals=[mg])
    ga = GoalArea(name="Exercise", phases=[ph])
    dumped = ga.model_dump()
    reloaded = GoalArea.model_validate(dumped)
    assert reloaded.phases[0].micro_goals[0].name == "Walk 5 min"


def test_checkin_success_ratio() -> None:
    mg = MicroGoal(name="Test")
    mg.checkins.extend([
        Checkin(date=date.today() - timedelta(days=i), success=True)
        for i in range(5)
    ])
    assert len(mg.checkins) == 5


def test_status_enum() -> None:
    assert Status.active.value == "active"
```

#### `tests/unit/test_json_store.py`

```python
from pathlib import Path

from microhabits.core.models import GoalArea
from microhabits.storage.json_store import JSONStore


def test_json_store_roundtrip(tmp_path: Path) -> None:
    store = JSONStore(path=tmp_path / "data.json")
    goals = [GoalArea(name="Sleep Hygiene")]
    store.save(goals)
    loaded = store.load()
    assert loaded[0].name == "Sleep Hygiene"
```

### 1‑5  Coverage & Static Analyse

Run:

```bash
pytest --cov=microhabits --cov-report=term-missing -q
ruff .
black --check .
mypy microhabits
```

All should pass with **≥ 90 %** coverage.

### 1‑6  Commit & Tag

Commit changes with message:

```
feat(core,storage): Phase 1 – data models + JSONStore with tests
```

Tag pre-alpha if desired: `git tag v0.1.0-alpha`.

---

🎉 **Phase 1 is complete** when:

* All tests & linters pass.
* Coverage ≥ 90 %.
* CLI `python -m microhabits --help` still exits 0.

Proceed to Phase 2 (CLI CRUD) only after the above checklist is green.
