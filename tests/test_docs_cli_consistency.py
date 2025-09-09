from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_docs_do_not_use_outdated_flags() -> None:
    readme = _text("README.md")
    tutorial = _text("TUTORIAL.md")
    body = readme + "\n" + tutorial

    # Flags that should no longer appear anywhere
    forbidden = [
        "--status",  # replaced by --success/--skip or --fail
        "--name ",  # micro add uses positional name
        "--cue ",
        "--scaffold ",
        "--target-time",
    ]
    for flag in forbidden:
        assert flag not in body, f"Outdated flag present in docs: {flag}"


def test_readme_quick_start_uses_supported_checkin_flags() -> None:
    readme = _text("README.md")
    # Expect one of the supported flags in the checkin example
    assert (
        "--success" in readme or "--skip" in readme or "--fail" in readme
    ), "README checkin example should use --success/--skip/--fail"


def test_readme_testing_section_claims_80_percent_gate() -> None:
    readme = _text("README.md")
    # Ensure we don't claim 100% coverage anywhere
    assert "100 % Test Coverage" not in readme
    # Ensure Testing & CI section mentions 80 %
    assert "80 %" in readme or "80%" in readme


def test_tutorial_micro_add_uses_positional_name() -> None:
    tutorial = _text("TUTORIAL.md")
    # Look for an example resembling: loopbloom micro add "Name" --goal ...
    assert re.search(r"loopbloom\s+micro\s+add\s+\".+\"", tutorial)
