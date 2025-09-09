"""Simple TOML-based user configuration.

Configuration files live under ``~/.config/loopbloom`` (or the directory
specified by ``XDG_CONFIG_HOME``) so multiple tools can share settings.
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict

import tomli_w
import tomllib
from pydantic import BaseModel

# Resolve the user's configuration directory (e.g. ``~/.config`` on Linux).
# Honour the ``XDG_CONFIG_HOME`` environment variable with a sensible default.
XDG_CONFIG_HOME = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
# Application-specific directory where LoopBloom stores its settings. The
# directory is created lazily by ``save`` to avoid side effects at import time.
APP_DIR = XDG_CONFIG_HOME / "loopbloom"
# Users may override ``CONFIG_PATH`` for testing by setting this variable.
# Full path to the TOML configuration file.
# Used by :func:`load` and :func:`save`.
CONFIG_PATH = APP_DIR / "config.toml"

# Built-in defaults used when ``config.toml`` does not exist or omits keys.
# New keys should be added here with sensible values so older configs remain
# valid after upgrades.
DEFAULTS: Dict[str, Any] = {
    # Persistence back-end. 'json' keeps everything in a file while 'sqlite'
    # stores data in a lightweight database.
    "storage": "json",  # json | sqlite
    # Optional path override for the selected storage back-end.
    # When empty, defaults described in README are used.
    "data_path": "",
    # How progress notifications are delivered.
    "notify": "terminal",  # terminal | desktop | none
    # Parameters for the auto-progression engine.
    "advance": {
        "threshold": 0.80,
        "window": 14,
        "strategy": "ratio",
        "streak_to_advance": 10,
    },
    # Notification pause settings
    "pause_until": "",  # ISO date string when global pause expires
    "goal_pauses": {},  # Mapping of goal name -> ISO date
}


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge ``b`` into ``a``.

    Args:
        a: Base dictionary which will receive updates.
        b: Dictionary whose values take precedence.

    Returns:
        dict: A new dictionary containing the merged result.
    """
    # ``b`` wins when keys collide, mirroring how ``dict.update`` works but
    # recursively for nested mappings.
    # We make a copy of ``a`` so callers keep their original unchanged.
    res = a.copy()
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(res.get(k), dict):
            # Merge nested dictionaries rather than overwriting them.
            res[k] = _deep_merge(res[k], v)
        else:
            # Non-dict values replace what's in ``a``.
            res[k] = v
    return res


def load() -> Dict[str, Any]:
    """Load the user configuration merged with built-in defaults."""
    # Missing files are treated as empty configs so first-run works without
    # requiring any setup from the user.
    if not CONFIG_PATH.exists():
        return DEFAULTS.copy()
    with CONFIG_PATH.open("rb") as fp:
        data = tomllib.load(fp)
    # Merge user values over the built-in defaults.
    return _deep_merge(DEFAULTS, data)


def save(new_cfg: Dict[str, Any]) -> None:
    """Persist ``new_cfg`` on disk after merging with defaults."""
    # ``_deep_merge`` ensures partial configs don't drop missing defaults.
    # This makes ``config set`` operations idempotent.
    merged = _deep_merge(DEFAULTS, new_cfg)
    # Ensure configuration directory exists when saving.
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("wb") as fp:
        tomli_w.dump(merged, fp)


class ProgressionStrategy(str, Enum):
    """Progression evaluation modes."""

    RATIO = "ratio"
    STREAK = "streak"


class ProgressionConfig(BaseModel):
    """Typed view over advancement settings."""

    threshold: float = 0.80
    window: int = 14
    strategy: ProgressionStrategy = ProgressionStrategy.RATIO
    streak_to_advance: int = 10
