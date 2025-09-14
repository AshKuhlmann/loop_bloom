Requirement: The pre-commit script must succeed before opening a pull request.
Rule: Do not modify the `scripts/pre-commit` script. Keep it as the canonical local gate.

Quick checklist before a PR:
- Install tooling: `pip install poetry`
- Install deps: `poetry install`
- Run checks: `./scripts/pre-commit`

Only open a PR once `./scripts/pre-commit` passes end-to-end. If any step fails, fix the issues and rerun until green.

Documentation alignment requirement:
- When you change code that affects user-facing behavior (CLI flags, command names, output formats, examples), you must update the documentation in the same change set.
- Keep `README.md`, `TUTORIAL.md`, and `USER_GUIDE.md` consistent with the current CLI. Examples must reflect real commands and supported flags.
- Prefer adding or updating lightweight tests that enforce doc–CLI consistency (see `tests/test_docs_cli_consistency.py`).
