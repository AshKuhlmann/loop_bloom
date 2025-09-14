
# LoopBloom CLI 🧩

*Compassion-first habit-building for ADHD brains and anyone who prefers **tiny, sustainable wins** over motivational hype.*

> **TL;DR**
> • Install once → pick goals → forget the spreadsheets.  
> • Define *micro-habits* that take ≤ 5 min.  
> • Log progress with a single command.  
> • The CLI talks *to you* (self-talk & encouragement), not the other way around.  
> • When you achieve **≥ 80 % success over 14 days**, it nudges you to level-up—gently.

---

## Table of Contents

1. [Why LoopBloom CLI?](#why)  
2. [Feature Highlights](#features)  
3. [Installation](#install)  
4. [Quick Start](#quick-start)  
5. [Sample Session](#sample)  
6. [Command Cheatsheet](#cheatsheet)  
7. [Configuration](#config)  
8. [Storage Back-Ends](#storage)  
9. [Coping Plans](#coping)  
10. [Progression Engine](#progression)  
11. [Notifications](#notifications)  
12. [Data Export](#export)  
13. [Developer Guide](#dev-guide)  
14. [Testing & CI](#testing)  
15. [Contributing](#contrib)  
16. [Changelog](#changelog)  
17. [License](#license)

---

<a id="why"></a>

## 1  Why LoopBloom CLI?

Traditional trackers assume unlimited will-power and demand elaborate setups. **LoopBloom CLI** is designed to be a **"set-and-forget" personal trainer**:

* **Zero spreadsheet anxiety** – one command creates goals; the app tracks everything.  
* **Strategic Effort > Endless Will-power** – focus on one doable habit at a time.  
* **Self-talk for you** – the tool generates compassionate, upbeat messages so you don’t have to.  
* **Slips ≠ Failure** – built-in self-compassion and fast re-engagement.  
* **Invisible Scaffolding** – cues, streak banners, notifications, and coping guides.

<a id="features"></a>

## 2  Feature Highlights

| Area                    | What you get                                                       | 
| ----------------------- | ------------------------------------------------------------------ | 
| **Hierarchical Goals**  | `goal → phase → micro` with reorder, cancel, edit.                 | 
| **Focused Check-ins**   | `checkin` automatically finds the one active micro-habit for a goal and records your progress on it in under 10 seconds. | 
| **Smart Progression**   | ≥ 80 % over 14 days triggers *advance* prompt.                     | 
| **Guided Coping**       | `cope` launches YAML Q\&A scripts for overwhelm.                   | 
| **Gentle Banners**      | `summary` prints streaks, nudges, celebrations. Optional `--goal`. | 
| **Tree View**           | `tree` shows your goals, phases, and micro-habits. |
| **Exports**             | \`export csv/json                                                  | 
| **Pluggable Storage**   | JSON by default; SQLite plugin for power-users.                    | 
| **Quality Gates**        | ≥ 80% coverage enforced; type checks and linting in CI.           | 

<a id="install"></a>

## 3  Installation

LoopBloom CLI requires Python >= 3.10.

### For End-Users
The recommended way to install is via pipx to ensure dependencies are isolated:

```bash
pipx install loopbloom-cli
```
Alternatively, you can use pip:

```bash
pip install loopbloom-cli
```

### For Contributors
To set up a development environment, you will need Poetry.

Clone the repository:
```bash
git clone https://github.com/ashkuhlmann/loopbloom-cli.git
```
Navigate into the project directory:
```bash
cd loopbloom-cli
```
Install dependencies with Poetry:
```bash
poetry install
```
Activate the virtual environment:
```bash
poetry shell
```
Once the environment is activated, you can run the CLI directly with the `loopbloom` command. Refer to `CONTRIBUTING.md` for more details.

### Shell Completions

Enable completions for faster CLI usage. Print the appropriate script and add it to your shell profile:

- Bash (add to ~/.bashrc or ~/.bash_profile):

  ```sh
  eval "$(_LOOPBLOOM_COMPLETE=bash_source loopbloom)"
  ```

- Zsh (add to ~/.zshrc):

  ```sh
  eval "$(_LOOPBLOOM_COMPLETE=zsh_source loopbloom)"
  ```

- fish (add to ~/.config/fish/config.fish):

  ```fish
  eval (env _LOOPBLOOM_COMPLETE=fish_source loopbloom)
  ```

- PowerShell (pwsh):

  ```powershell
  $Env:_LOOPBLOOM_COMPLETE = 'powershell'; loopbloom | Out-String | Invoke-Expression; Remove-Item Env:_LOOPBLOOM_COMPLETE
  ```

You can also detect your shell or select it explicitly:

```bash
loopbloom completion            # auto-detect
loopbloom completion zsh        # explicit
```

<a id="quick-start"></a>

## 4  Quick Start

For a step-by-step walkthrough, see the [Getting Started Tutorial](TUTORIAL.md).

```bash
# 1  Create a goal area
loopbloom goal add "Sleep Hygiene"

# 2  Add a micro-habit (≤ 5 min!)
# The name of the micro-habit is a positional argument.
loopbloom micro add "Wake up at 08:00" --goal "Sleep Hygiene"

# 3  Begin tracking each day
# This command will find the currently active micro-habit under "Sleep Hygiene" (which is "Wake up at 08:00") and record a successful check-in for it.
loopbloom checkin "Sleep Hygiene" --success --note "Groggy but did it!"
```

The CLI replies with something like:

```
✓ Logged!  🎉  Your consistency is paying off—great job showing up even when groggy.
```

<a id="sample"></a>

## 5  Sample Session

<details>
<summary>Click to expand</summary>

```console
$ loopbloom summary
┏━━━━━━━━━━━━━━━━━━━━━━━ LoopBloom ━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Goal            Streak   Last 14 Days   Next Action       ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Sleep Hygiene   ▇▇▇▇▇▇▇▇  10/14 (71 %)   Stay the course ✨ ┃
┃ Exercise        ▇▇▇▁▇▇▇▇  12/14 (86 %)   Advance? (type Y) ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
Tip: `loopbloom summary --goal "Exercise"` for details.

$ loopbloom summary --goal "Exercise"
Goal: Exercise → Micro #1 "Walk 5 min"
• Success rate: 86 % (last 14 days)
• Auto-advance suggestion: ➜ "Walk 6 min"  (accept? [Y/n])

$ loopbloom checkin "Exercise" --skip --note "Rainy" 
⚠️  Skipped today. Mini-pep-talk: “A single rainy day doesn’t wash away progress—see you tomorrow!”

$ loopbloom cope run overwhelmed
👉  Identify the biggest stressor right now:  _inbox backlog_
👉  Pick one micro-action that would lighten it by 1 %:  _triage 5 emails_
💬  Great job—action dispels anxiety. 💪
```

</details>

<a id="cheatsheet"></a>

## 6  Command Cheatsheet

```text
loopbloom help                         # global help

GOALS & MICRO-HABITS
  loopbloom goal  list|add|edit|rm                # manage goal areas
  loopbloom goal phase add|rm                    # manage phases
  loopbloom micro list|add|edit|rm|complete|cancel   # micro-habit operations
  loopbloom tree                         # show goal hierarchy

CHECK-INS & FEEDBACK
  loopbloom checkin   <goal_name> [--success|--skip|--fail] [--note ..]
  loopbloom summary   [--goal <name>]   # streak banner, next steps
  loopbloom review    [--period day|week]   # reflect on progress

COPING & SUPPORT
  loopbloom cope list           # view plan names
  loopbloom cope run <name>     # guided coping walkthrough
  loopbloom cope new            # interactive plan creator

DATA & CONFIG
  loopbloom export --fmt csv|json --out progress.csv
  loopbloom config set key val | get key | view
```

<a id="config"></a>

## 7  Configuration

Settings live in `~/.config/loopbloom/config.toml` (XDG). Example:

```toml
storage = "json"            # json | sqlite
data_path = ""              # optional override for data file
notify  = "terminal"        # terminal | desktop | none
advance.threshold = 0.80    # float (0-1)
advance.window    = 14       # days
```

CLI shortcut: `loopbloom config set storage sqlite`.

<a id="storage"></a>

## 8  Storage Back-Ends

| Backend                                                              | Path                     | Use-case                             |
| -------------------------------------------------------------------- | ------------------------ | ------------------------------------ |
| **JSON** (default)                                                   | `~/.config/loopbloom/data.json` | Simple, git-friendly.                |
| **SQLite**                                                           | `~/.config/loopbloom/data.db`   | Large histories, multi-tool queries. |
| Custom stores implement the `Storage` protocol in `storage/base.py`. |                          |                                      |

Set `data_path` in `config.toml` or use `LOOPBLOOM_DATA_PATH`/`LOOPBLOOM_SQLITE_PATH` to keep data elsewhere.
<a id="coping"></a>

## 9  Coping Plans

Built-in scripts live in `loopbloom/data/coping/*.yml` and power
`loopbloom cope run <name>`. Create your own plans with
`loopbloom cope new`—the CLI will prompt for a title and steps, then
save a YAML file you can edit later.

<a id="progression"></a>

## 10  Progression Engine

```mermaid
flowchart TD
    Checkin -- emits --> EventBus
    EventBus --> Progression[progression.eval()]
    Progression -->|>= 80% / 14d| AdvanceBanner
    Progression -->|otherwise| CompassionateNudge
```

Parameters `threshold` and `window` are user-configurable.
When omitted by commands, the progression rule reads these values from
`~/.config/loopbloom/config.toml`.

<a id="notifications"></a>

## 11  Notifications

Terminal banners by default; desktop via `plyer` (`loopbloom config set notify desktop`).

### Troubleshooting: macOS Desktop Notifications

On macOS, the optional `plyer` backend may rely on platform-specific bridges (e.g., `pyobjus`). If these are unavailable, LoopBloom will fall back to terminal notifications automatically. To explicitly avoid desktop integrations (useful on headless or minimal setups), set the notify mode to terminal:

```bash
loopbloom config set notify terminal
```

Switch back any time with:

```bash
loopbloom config set notify desktop
```

<a id="export"></a>

## 12  Data Export

```bash
loopbloom export --fmt csv --out ~/Desktop/loopbloom_progress.csv
```

<a id="dev-guide"></a>

## 13  Developer Guide (Brief)

*Thin CLI → Service → Core → Storage* layered architecture; see [USER_GUIDE.md](USER_GUIDE.md) for full docs.

### Debugging

Enable debug mode on any command with `--debug` to see verbose logging and
extra diagnostics. Use `--dry-run` to preview changes without saving them.
The application date can be overridden for testing by setting the
`LOOPBLOOM_DEBUG_DATE` environment variable (YYYY-MM-DD). To dump the raw
goal state run `loopbloom debug-state`.

### Testing Interactive Commands
Several commands like `cope new` or `goal wizard` are interactive. While the integration test suite uses input redirection to test these flows (see `tests/integration/test_cope_new.py` and `tests/integration/test_goal_wizard.py`), running these within automated scripts that cannot provide interactive input may be challenging. We recommend using Click's testing utilities for robust testing of interactive prompts.

<a id="testing"></a>

## 14  Testing & CI

CI enforces a minimum of 80 % unit and integration test coverage.

<a id="contrib"></a>

## 15  Contributing

PRs welcome—see `CONTRIBUTING.md`.

<a id="changelog"></a>

## 16  Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
