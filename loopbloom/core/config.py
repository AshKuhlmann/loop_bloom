"""Simple TOML-based user configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import tomli_w
import tomllib

XDG_CONFIG_HOME = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
# Allow tests to override full path directly
CONFIG_PATH = Path(
    os.getenv(
        "LOOPBLOOM_CONFIG_PATH",
        XDG_CONFIG_HOME / "loopbloom" / "config.toml",
    )
)
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

DEFAULTS: Dict[str, Any] = {
    "storage": "json",  # json | sqlite
    "notify": "terminal",  # terminal | desktop | none
    "advance": {"threshold": 0.80, "window": 14},
}


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge dict ``b`` into ``a`` and return result."""
    res = a.copy()
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(res.get(k), dict):
            res[k] = _deep_merge(res[k], v)
        else:
            res[k] = v
    return res


def load() -> Dict[str, Any]:
    """Return config merged with defaults."""
    if not CONFIG_PATH.exists():
        return DEFAULTS.copy()
    with CONFIG_PATH.open("rb") as fp:
        data = tomllib.load(fp)
    return _deep_merge(DEFAULTS, data)


def save(new_cfg: Dict[str, Any]) -> None:
    """Persist NEW_CFG merged with defaults."""
    merged = _deep_merge(DEFAULTS, new_cfg)
    with CONFIG_PATH.open("wb") as fp:
        tomli_w.dump(merged, fp)
