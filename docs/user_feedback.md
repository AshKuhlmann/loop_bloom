# User Feedback for LoopBloom CLI

Note: This document captures historical feedback, some of which predates recent
improvements. Installation, command names, and flags referenced below may have
since been updated. Refer to the README, Tutorial, and User Guide for the
canonical, up-to-date usage.

## Evaluation Results

I performed a series of workflow simulations based on the `README.md` to evaluate the LoopBloom CLI.

### What Went Well

*   **Installation (once dependencies were resolved):** After addressing initial dependency issues, the application ran smoothly without further module errors.
*   **Goal and Micro-habit Addition (with correct syntax):** The `goal add` and `micro add` commands functioned as expected when the correct syntax (positional arguments for names, and specific flags) was used.
*   **Check-in Functionality:** The `checkin` command successfully recorded successes and skips, providing appropriate feedback and progression summaries. The compassionate messages for skips are a well-implemented feature.
*   **Summary and Tree Views:** The `summary` and `tree` commands delivered clear, well-formatted, and useful overviews of goals and their hierarchical structure and progress.
*   **Configuration Management:** The `config set` and `config view` commands worked correctly for managing application settings.
*   **Data Export:** The `export` command successfully exported data to the specified format and location.
*   **Use of `LOOPBLOOM_DEBUG_DATE`:** This environment variable proved very helpful for simulating time-based progression and testing without affecting real-time data.
*   **Use of `LOOPBLOOM_DATA_PATH`:** This environment variable was crucial for isolating test data from the user's actual data, ensuring a safe testing environment.

### What Went Wrong / Bugs / Improvements Recommended

1.  **Significant Discrepancy between `README.md` and Actual CLI Usage:** This was the most prominent issue encountered during the evaluation, leading to initial confusion and errors.

    *   **`loopbloom` Command Execution:** The `README.md` implies `loopbloom` is directly executable (e.g., `loopbloom goal add`), but it required `python -m loopbloom` to run.
        *   **Recommendation:** Update the "Installation" and "Quick Start" sections of the `README.md` to explicitly state that the command should be run as `python -m loopbloom`.

    *   **`micro add` Command Options:** The `README.md`'s "Quick Start" example for `micro add` (`loopbloom micro add --goal "Sleep Hygiene" --name "Wake up at 08:00" --cue "After alarm" --scaffold "Alarm+Sunlight" --target-time 08:00`) is inconsistent with the actual CLI behavior.
        *   `--name` is not an option; the micro-habit name is a positional argument.
        *   `--cue`, `--scaffold`, and `--target-time` are not supported options for `micro add`. Furthermore, there is no `micro edit` command to add these details later.
        *   **Recommendation:** Update the `README.md` to reflect the current `micro add` syntax. If `cue`, `scaffold`, and `target-time` are intended features for micro-habits, they need to be implemented (perhaps via a `micro edit` command or interactive prompts during `micro add`) and then accurately documented.

    *   **`checkin` Command Options:** The `README.md`'s "Quick Start" example for `checkin` (`loopbloom checkin --goal "Sleep Hygiene" --status done --note "Groggy but did it!"`) is also inconsistent.
        *   `--goal` is not an option; the goal name is a positional argument.
        *   `--status done` and `--status skip` are replaced by `--success` and `--skip` flags, respectively.
        *   **Recommendation:** Update the `README.md` to reflect the current `checkin` syntax.

    *   **General Documentation Recommendation:** A comprehensive review and update of all command examples and syntax across the `README.md` and any other user-facing documentation (e.g., `TUTORIAL.md`, `USER_GUIDE.md`) is strongly recommended to ensure consistency with the current CLI implementation.

2.  **Dependency Management/Installation Process:**
    *   The initial `ModuleNotFoundError: No module named 'tomli_w'` indicated that the project's dependencies were not installed. While `poetry install` resolved this, the user first had to install `poetry` itself, which was not explicitly mentioned as a prerequisite in the `README.md`.
    *   **Recommendation:** The "Installation" section of `README.md` should clearly state `poetry` as a prerequisite and provide instructions for installing `poetry` if it's not already present, before instructing users to run `poetry install`. Alternatively, if `pip install loopbloom-cli` is intended to be a complete installation solution, then the `pyproject.toml` needs to ensure all necessary packages are listed as direct dependencies that `pip` will install.

3.  **Interactive Commands Simulation:**
    *   Interactive commands such as `cope run` and `cope new` could not be fully simulated during this evaluation due to the limitations of the `run_shell_command` tool, which does not support interactive input. This is a limitation of the testing environment, not necessarily a bug in the CLI itself.
    *   **Recommendation:** For future automated testing of interactive CLI features, consider using a testing framework or tool that can simulate interactive input. If feasible, providing non-interactive alternatives for such commands could also enhance usability for scripting or automated workflows.

4.  **`checkin` Granularity:**
    *   The `checkin` command appears to check in for a single micro-habit (specifically, the first active one) associated with a goal, rather than allowing a check-in for the goal as a whole, which might be implied by the `README.md`'s "Fast Check-ins" description.
    *   **Recommendation:** Clarify in the documentation how `checkin` handles multiple micro-habits under a single goal. If the intention is to check in for all active micro-habits under a goal, the functionality needs to be adjusted. If it's by design to check in one by one, then the documentation should explicitly state this behavior.
