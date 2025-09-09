import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _min_version_from_pyproject(pyproject_text: str) -> str:
    """Extract the declared minimum Python version from pyproject.

    Supports caret (e.g., ^3.10) and >= specs (e.g., ">=3.10"). Returns
    major.minor string, e.g., "3.10".
    """
    m = re.search(r"^python\s*=\s*\"([^\"]+)\"", pyproject_text, re.MULTILINE)
    assert m, "python requirement not found in pyproject.toml"
    spec = m.group(1).strip()
    # Accept patterns like ^3.10, >=3.10, >=3.10,<4.0
    if spec.startswith("^"):
        ver = spec[1:]
        # ^3.10 or ^3.10.* → take first two components
        parts = ver.split(".")
        return f"{parts[0]}.{parts[1]}"
    if spec.startswith(">="):
        ver = spec.split(",")[0][2:]
        parts = ver.split(".")
        return f"{parts[0]}.{parts[1]}"
    raise AssertionError(f"Unsupported python version spec: {spec}")


def _min_version_from_text(text: str) -> str | None:
    """Try to find a 'Python >= X.Y' or 'Python 3.Y or later' mention."""
    # Pattern 1: Python >= 3.10
    m = re.search(r"Python\s*>=\s*3\.(\d{1,2})", text)
    if m:
        return f"3.{m.group(1)}"
    # Pattern 2: Python 3.10 or later
    m = re.search(r"Python\s*3\.(\d{1,2})\s*or\s*later", text, flags=re.IGNORECASE)
    if m:
        return f"3.{m.group(1)}"
    return None


def test_docs_min_python_matches_pyproject() -> None:
    py_min = _min_version_from_pyproject(_read(ROOT / "pyproject.toml"))

    readme_min = _min_version_from_text(_read(ROOT / "README.md"))
    assert readme_min is not None, "README should mention minimum Python version"
    assert (
        readme_min == py_min
    ), f"README min version {readme_min} != pyproject {py_min}"

    tutorial_min = _min_version_from_text(_read(ROOT / "TUTORIAL.md"))
    assert tutorial_min is not None, "TUTORIAL should mention minimum Python version"
    assert (
        tutorial_min == py_min
    ), f"TUTORIAL min version {tutorial_min} != pyproject {py_min}"


def test_ci_matrix_includes_min_python() -> None:
    py_min = _min_version_from_pyproject(_read(ROOT / "pyproject.toml"))
    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_path.exists(), "CI workflow missing"

    ci = yaml.safe_load(_read(ci_path))
    jobs = ci.get("jobs", {})
    assert "ci" in jobs, "Expected 'ci' job in workflow"
    strategy = jobs["ci"].get("strategy", {})
    matrix = strategy.get("matrix", {})
    versions = matrix.get("python-version")
    assert isinstance(
        versions, list
    ), "CI should define a matrix of python-version values"
    # Ensure declared min version is present and there is at least one higher version
    assert py_min in versions, f"CI matrix should include min version {py_min}"
    assert any(v != py_min for v in versions), "CI should test multiple versions"
