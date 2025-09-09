# 2025-09-09 — LoopBloom CLI Review Checklist

Below is an actionable checklist capturing the review, fixes applied, and suggested improvements across code, docs, UX, dependencies, and CI.

## Completed Today

- [x] Remove import-time file system writes (avoid sandbox/CI PermissionError):
  core/config.py, constants.py, storage/json_store.py, storage/sqlite_store.py, core/review.py, core/journal.py.
- [x] Make logging robust in restricted environments (fallback to stderr when logs dir is not writable).
- [x] Fix ruff/black/mypy issues (sorted imports, removed unused imports, type narrowing in cli/checkin; safe access to store path in cli/config via cast).
- [x] Format with black; re-run full pre-commit pipeline.
- [x] Run tests (116 passing; coverage ~90.47% ≥ 80% threshold).
- [x] Validate packaging (pip install .) flows.

## High-Priority Improvements

- [x] Align Python version across repo:
  - Decision: support Python ≥ 3.10 (code uses `|` unions from 3.10).
  - Updated pyproject to `python = "^3.10"` and docs (README/TUTORIAL).
  - CI updated to run a single Python (3.11) per repo policy.
- [x] Replace deprecated Pydantic serialization:
  - Stop using `pydantic.json.pydantic_encoder` and switch to `model_dump(mode="json")` and/or `pydantic_core.to_jsonable_python`.
  - Updated: `storage/json_store.py`, `core/review.py`, `core/journal.py` to emit JSON via `model_dump(mode="json")`.
  - Updated tests to drop `pydantic_encoder`; confirmed no Pydantic deprecation warnings; all tests green.
- [ ] Update ruff config to new schema:
  - Move `[tool.ruff].select` → `[tool.ruff.lint].select` to silence deprecation warnings.
- [ ] Update docs to match actual CLI:
  - Tutorial: `micro add` uses positional name plus `--goal` (and `--phase`), not `--name/--cue/--scaffold/--target-time`.
  - Tutorial/README: `checkin` uses `--success/--skip` or `--fail`, not `--status done`.
  - README: replace “100% Test Coverage” claim with accurate statement (e.g., “≥ 80% enforced; current ~90%”).
- [ ] Pre-commit packaging step:
  - In `scripts/pre-commit`, replace `python -m pip install .` with `poetry run python -m pip install .` to avoid extra network resolution outside the venv.
  - Optionally drop the packaging step from local pre-commit and keep it in CI.
- [ ] Expose data path via Storage protocol:
  - Add `path: Path` or `data_path() -> Path` to `Storage` to remove casts to access private `_path`.
- [ ] Trim and structure dependencies:
  - Remove unused deps (e.g., `typer`, `beartype`) if truly unused.
  - Deduplicate `tomli-w` (present in main and dev groups).
  - Consider extras: `sqlite` (sqlalchemy, aiosqlite), `report` (plotext) to reduce default footprint.
- [ ] Logging behavior policy:
  - Make file logging opt-in or controlled by an env var; keep stderr default for portability.

## CLI/UX Enhancements

- [ ] Add `checkin --date YYYY-MM-DD` to log for a specific day (coexists with `LOOPBLOOM_DEBUG_DATE`).
- [ ] Add `checkin undo` and/or `checkin edit --date --status --note` to amend mistakes.
- [ ] Add `loopbloom status` command to show backend, data path, notify mode, and active pauses.
- [ ] Provide shell completions (Click supports), e.g., `loopbloom completion`.
- [ ] Normalize help text around `--skip` vs `--fail` for clarity and consistency.
- [ ] Notifications: add a simple `pause status` output and clearer messaging when desktop notify fails (with quiet fallback).

## Reports, Data & Templates

- [ ] Add `report --mode table` (ASCII) and `--fmt markdown` for table exports.
- [ ] Add `import` for CSV/JSON produced by LoopBloom (bootstrap from other trackers).
- [ ] Provide optional goal templates (e.g., Sleep Hygiene) that create phased micro-habits with one command.
- [ ] Consider advanced progression UX: surface per-micro `threshold/window` in CLI and add commands to inspect/set overrides.

## CI/CD & Quality Gates

- [ ] CI workflow mirroring `scripts/pre-commit`:
  - poetry install, ruff, black --check, mypy, pytest with coverage ≥ 80%.
  - Add packaging step (`poetry run python -m pip install .`).
  - Cache Poetry and pytest artifacts for speed.
- [ ] Optionally publish dev/nightly wheels for install validation.
- [ ] Temporarily filter Pydantic deprecation warnings in tests until serialization is updated (to keep signal clean).

## Nice-to-Have / Exploratory

- [ ] Scheduling/reminders: document simple cron/launchd snippets; consider a thin integration later.
- [ ] Storage evolution: if denormalizing in SQLite later, outline a minimal migration path (not urgent now).
- [ ] Evaluate dependency footprint regularly; keep startup and install snappy for end-users.
