Requirement: The pre-commit script must succeed before opening a pull request.
Rule: Do not modify the `scripts/pre-commit` script. Keep it as the canonical local gate.

Quick checklist before a PR:
- Install tooling: `pip install poetry`
- Install deps: `poetry install`
- Run checks: `./scripts/pre-commit`

Only open a PR once `./scripts/pre-commit` passes end-to-end. If any step fails, fix the issues and rerun until green.
