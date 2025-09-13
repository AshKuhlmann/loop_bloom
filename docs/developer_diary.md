# 2025-09-13 — LoopBloom CLI Deep-Dive Roadmap

This entry captures a comprehensive, actionable improvement roadmap spanning architecture, UX, robustness, performance, testing, docs, and delivery. Items are phrased as concrete checklists to enable steady, traceable progress.

## Architecture & Design

- [ ] Define an explicit `Storage` capability for data path discovery (e.g., `data_path() -> Path`) to eliminate casts to private attributes.
- [ ] Ensure CLI command registration is idempotent (avoid double `register_commands()` calls). Consider a guard flag or register lazily on first invocation.
- [ ] Add a lightweight domain service layer façade (e.g., `GoalService`) to reduce repeated goal/phase/micro traversal logic across CLI modules.
- [ ] Introduce module-level dependency boundaries (CLI → services → core → storage) via linting rules or import linter configuration.
- [ ] Consider a minimal plugin architecture (entry points) for future extensions (e.g., third-party reports, custom exporters, notification backends).

## Domain Models & Validation

- [ ] Make datetimes timezone-aware or consistently naive (UTC vs local). Currently `created_at` uses `utcnow()` while check-ins use local dates.
- [ ] Add invariants: prevent multiple active micro-habits per goal/phase by helper methods that enforce single-active semantics.
- [ ] Provide helper to add a check-in that deduplicates same-day duplicates per micro-habit unless explicitly permitted with `--allow-duplicate`.
- [ ] Promote `ProgressionConfig` to a first-class read path in code (typed accessors instead of dict lookups).
- [ ] Validate `advancement_window` and `advancement_threshold` ranges when set via CLI (min/max and type checks).

## CLI/UX & Ergonomics

- [ ] Add `checkin --date YYYY-MM-DD` to backfill or correct past days.
- [ ] Add `checkin undo` and `checkin edit --date --success/--skip --note` for corrections.
- [ ] Add `loopbloom status` printing: storage backend, data path (resolved), notify mode, pause flags, active goal/micro.
- [ ] Add `completion` command to generate shell completions (bash/zsh/fish/pwsh).
- [ ] Normalize terminology: `--skip` and `--fail` aliases are fine; unify help text and examples for consistency.
- [ ] In `tree`, annotate micro-habits with status glyphs (active ✓ / complete ✔ / cancelled ✖) and optionally counts (check-ins last N days).
- [ ] Provide `--json` output for key commands (`goal list`, `summary`, `report`) to support scripting.

## Progression Engine

- [ ] Expose CLI to set per-micro overrides: `micro set --window N --threshold X.Y` and `--strategy ratio|streak --streak-to-advance N`.
- [ ] Add a dry-run progression preview: `summary --goal X --explain` returning exact reasons and what is missing (already present internally; expose nicely).
- [ ] Add guardrails so a change in window/strategy does not retroactively misinterpret historical data (document this clearly).
- [ ] Optionally support “grace days” or weighted recent days to smooth decisions.

## Storage Layer (JSON & SQLite)

- [ ] JSON: add optional file locking (e.g., `fcntl`/`msvcrt` or `portalocker`) to protect from concurrent writes if users script multiple processes.
- [ ] JSON: consider streaming writes or temp-file + atomic rename (already atomic via write-then-replace; confirm on Windows).
- [ ] SQLite: store payload as `Text` instead of `String` to avoid length ambiguity; consider a versioned schema with migrations if denormalization changes.
- [ ] Provide a `migrate` command for JSON→SQLite and back, including verification (`hash` of logical content) and backup.
- [ ] Add integrity check command: verify model round-trip on current backend (`load`→`dump`→`load`).

## Configuration & Settings

- [ ] Replace ad-hoc dict gets with typed accessors (`ProgressionConfig`) and defaults centralized in one place.
- [ ] Add schema validation for config file using Pydantic or `jsonschema` on load (with helpful errors and auto-fix suggestions).
- [ ] Support environment variable overrides consistently, documenting precedence (ENV > CLI > config > defaults) and applying uniformly to JSON/SQLite paths.
- [ ] Add `config unset <key>` and `config edit` (open in `$EDITOR`).
- [ ] Consider `notify` tri-state: terminal | desktop | none; already present—add `config validate` to report misconfigurations.

## Notifications

- [ ] Add macOS/Linux native fallbacks (osascript/dbus) if `plyer` unavailable; keep current fallback to terminal.
- [ ] Add `pause status` and `pause clear [--goal]` commands for transparency and quick unpause.
- [ ] Rate-limit or group notifications within a short time window to avoid spam if multiple commands run in a script.
- [ ] Optional encryption or redaction for sensitive journal/pep-talk content echoed to terminal (user setting).

## Reporting & Visualization

- [ ] Offer `report --mode table` and `--fmt markdown` to print portable summaries.
- [ ] Add `report --goal X` filters to focus charts (calendar/line) per goal.
- [ ] Handle terminals without Unicode by offering ASCII-only mode via env/flag.
- [ ] Consider embedding small sparkline sequences in `summary` rows.

## Coping Plans

- [ ] Add YAML schema validation (keys allowed: `id`, `title`, `steps`, each step has `prompt` xor `message`, optional `store_as`).
- [ ] Support conditional steps (simple `{if var}...{endif}` template blocks) or branching via minimal expressions.
- [ ] Add export/import/sync for user-defined plans; include a curated plan gallery.
- [ ] Add `cope run` transcript logging to a separate file (with opt-out) for reflective review.

## Observability & Logging

- [ ] Make file logging opt-in; default to stderr with level from env (`LOOPBLOOM_LOG_LEVEL`).
- [ ] Add a `--log-file` CLI option or config key to direct logs explicitly.
- [ ] Standardize structured logging fields (goal, phase, micro, checkin_date) for grepability.
- [ ] Add debug breadcrumbs for storage path selection precedence (env vs config vs defaults).

## Performance & Scalability

- [ ] Benchmark JSON vs SQLite round-trips at various sizes (1k/10k check-ins) and document guidance.
- [ ] Consider incremental JSON writes (append log of check-ins) with periodic compaction if needed.
- [ ] Cache loaded pep-talks and coping plans (already cached for talks) with invalidation on file mtime change.

## Reliability & Data Integrity

- [ ] Add fsync/flush options on save for users concerned with sudden power loss.
- [ ] Validate data files on startup; if corrupt, provide a recovery assistant pointing to the most recent backup.
- [ ] Add `backup --retention N` and `backup prune` to manage old archives.
- [ ] Provide `restore <backup-file>` command with confirmation and automatic current-backup creation.

## Security & Privacy

- [ ] Offer optional local encryption for journals/reviews (e.g., age/sops integration) or at-rest key via OS keychain.
- [ ] Ensure paths from env/config are sanitized; guard against accidental directory traversal in future import commands.
- [ ] Document data footprint and privacy posture clearly in README.

## Packaging & Distribution

- [ ] Remove unused dependencies (`typer`, `beartype`) if not used; convert extras (`plotext`, `sqlalchemy`, `aiosqlite`) into optional groups.
- [ ] Add `poetry export --with dev` guidance for contributors who prefer `pip` + venv.
- [ ] Provide a `pipx` install snippet prominently in README; verify `loopbloom` entry point works cross-platform.
- [ ] Automate version bump + changelog generation (e.g., `towncrier` or `git-cliff`).

## Testing Strategy

- [ ] Add property-based tests (Hypothesis) for progression edge-cases (window/threshold/streak interactions).
- [ ] Add fuzzy tests for name matching/suggestion UX in `cli.utils` with varied casing/spacing.
- [ ] Add tests for notification pause boundaries (today vs tomorrow vs invalid date strings) and error paths.
- [ ] Add tests for JSON/SQLite integrity checks and migration command once added.
- [ ] Consider snapshot tests for `tree`/`summary` outputs with Unicode and ASCII modes.

## CI/CD & Tooling

- [ ] Expand matrix to run on min and current Python versions (3.10, 3.11), and on macOS/Windows for CLI rendering parity.
- [ ] Cache Poetry and `~/.cache/pip` for faster CI runs; cache `.pytest_cache` where beneficial.
- [ ] Run `poetry run python -m pip install .` in CI to validate package installability in the same venv.
- [ ] Optionally wire Renovate/Dependabot to track dependency updates (pin major bumps behind PR).

## Documentation

- [ ] Add “Storage and Backups” guide with restore walkthrough and migration notes.
- [ ] Expand “Notifications” section to cover desktop fallbacks and pause semantics with examples.
- [ ] Provide an “Advanced Configuration” page with all env vars and precedence rules.
- [ ] Include a compact “Cheat Sheet” printable in `docs/` and referenced in README.
- [ ] Add Architecture Overview diagram (CLI → services → core → storage) in `docs/`.

## Developer Experience

- [ ] Add `make` targets (`make test`, `make lint`, `make format`, `make ci`) mirroring `scripts/pre-commit`.
- [ ] Add `justfile` alternative for Windows users who prefer `just`.
- [ ] Provide a minimal `CONTRIBUTING quickstart` snippet near the top with the 3 commands required locally.
- [ ] Add `pre-commit` (framework) config if desired; or keep current script but document the choice explicitly.

## Cross-Platform & Accessibility

- [ ] Confirm Windows path handling in backup/restore and JSON atomic writes; add tests under Windows in CI.
- [ ] Provide an ASCII-only mode to avoid rendering issues in restricted terminals.
- [ ] Consider color-blind-friendly palettes for charts/banners if/when color encodings expand.

## Roadmap & Extensions

- [ ] Optional “nudges” engine: time-of-day reminders tied to specific goals (document cron examples first).
- [ ] Simple HTTP/REST shim for reading summaries (read-only) so users can wire dashboards.
- [ ] Event hooks (pre/post check-in) to integrate with scripts (e.g., log to a separate file).


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
- [x] Update ruff config to new schema:
  - Move `[tool.ruff].select` → `[tool.ruff.lint].select` to silence deprecation warnings.
  - Added tests (`tests/unit/test_ruff_config_schema.py`) to enforce new schema and ensure deprecated keys are absent.
- [x] Update docs to match actual CLI:
  - Tutorial: `micro add` uses positional name plus `--goal` (and `--phase`), not `--name/--cue/--scaffold/--target-time`.
  - Tutorial/README: `checkin` uses `--success/--skip` or `--fail`, not `--status done`.
  - README: replace “100% Test Coverage” claim with accurate statement (≥ 80% enforced; current ~90%).
  - Added enforcement tests (`tests/test_docs_cli_consistency.py`).
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
