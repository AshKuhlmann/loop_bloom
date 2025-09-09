from __future__ import annotations

import tomllib


def test_ruff_lint_section_present_and_select_valid() -> None:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    ruff = data.get("tool", {}).get("ruff", {})
    # New schema should have a nested `lint` table
    assert "lint" in ruff, "[tool.ruff.lint] section is missing"
    lint = ruff["lint"]
    assert isinstance(lint.get("select"), list), "lint.select must be a list"
    # Ensure we still lint with the intended rule sets
    for code in ["E", "F", "I", "B", "W"]:
        assert code in lint["select"], f"Missing '{code}' in lint.select"


def test_no_top_level_select_in_tool_ruff() -> None:
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)

    ruff = data.get("tool", {}).get("ruff", {})
    # The deprecated top-level `select` should not be present anymore
    assert "select" not in ruff, "Deprecated [tool.ruff].select remains in config"
