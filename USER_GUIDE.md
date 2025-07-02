# LoopBloom User Guide

## Architecture Overview

LoopBloom is organised into a thin **CLI** layer on top of reusable libraries.
Commands talk to small service helpers which in turn rely on the **core** domain
modules and a pluggable **storage** layer.

```
CLI commands → service utilities → core logic → storage back‑ends
```

Each layer has a clear responsibility and only depends on the layer below it.
This separation keeps the CLI small while making core functionality available to
other front‑ends in the future.

## Module Responsibilities

### CLI (`loopbloom/cli`)
- Implements individual commands using [Click](https://click.palletsprojects.com/).
- Uses the `with_goals` decorator to load and save data via the selected storage
  backend.
- Commands are grouped by topic (`goal`, `micro`, `checkin`, etc.) and registered
  in [`__main__.py`](loopbloom/__main__.py).

### Services (`loopbloom/services`)
- Hosts helpers that provide side effects or integration with the operating
  system.
- Example: [`notifier.py`](loopbloom/services/notifier.py) sends desktop or
  terminal notifications depending on configuration.

### Core (`loopbloom/core`)
- Contains domain models and business rules used by all interfaces.
- Key modules include `models.py` for the goal/phase/micro-habit hierarchy,
  `config.py` for loading user settings, `progression.py` for advancement logic
  and `coping.py` for YAML-based coping plans.

### Storage (`loopbloom/storage`)
- Defines the abstract [`Storage`](loopbloom/storage/base.py) protocol.
- Provides concrete implementations: [`JSONStore`](loopbloom/storage/json_store.py)
  and [`SQLiteStore`](loopbloom/storage/sqlite_store.py).
- The CLI selects which backend to use at runtime based on `config.toml`.

## Extending the CLI

1. Create a new module under `loopbloom/cli/` and implement your Click command
   or group. Reuse helpers like `with_goals` or `click.pass_obj` to access data
   and configuration.
2. Import your command in [`__main__.py`](loopbloom/__main__.py) and register it
   with `cli.add_command(new_cmd)`. The ordering here controls the help display.
3. Add unit or integration tests under `tests/` covering the new behaviour.
4. Update documentation if the command is user-facing.

Following this pattern keeps the command surface thin while leveraging the
shared service, core and storage layers.
