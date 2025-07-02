# Contributing

Thank you for taking the time to contribute to **LoopBloom CLI**!

## Development Environment

This project uses [Poetry](https://python-poetry.org/) for dependency management. After cloning the repository, run:

```bash
poetry install
```

This creates a virtual environment and installs all development dependencies. You can enter the shell with:

```bash
poetry shell
```

From inside the environment (or by prefixing commands with `poetry run`), you can run all tooling and tests.

## Linting

- **Ruff** – fast linter and formatter:
  ```bash
  poetry run ruff check .
  ```
- **Flake8** – style and import checks:
  ```bash
  poetry run flake8
  ```

## Type Checking

Run [mypy](https://mypy-lang.org/) in strict mode:

```bash
poetry run mypy loopbloom
```

## Running Tests

Execute the full test suite with `pytest`:

```bash
poetry run pytest
```

## Pre-Commit Helper

For convenience, a helper script combines linting, type checks and tests. Run it before committing:

```bash
./scripts/pre-commit
```

It fails if any step does not pass, mirroring the checks that run in CI.

## Submitting Pull Requests

1. Fork the repository on GitHub and create a feature branch.
2. Commit your changes with clear messages and push the branch to your fork.
3. Open a Pull Request against the `main` branch and describe your changes.
4. Ensure CI passes before requesting review.

We appreciate every contribution!
