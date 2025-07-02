
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
| **Fast Check-ins**      | `checkin` records ✓/✕ & note in <10 s—CLI responds with self-talk. | 
| **Smart Progression**   | ≥ 80 % over 14 days triggers *advance* prompt.                     | 
| **Guided Coping**       | `cope` launches YAML Q\&A scripts for overwhelm.                   | 
| **Gentle Banners**      | `summary` prints streaks, nudges, celebrations. Optional `--goal`. | 
| **Tree View**           | `tree` shows your goals, phases, and micro-habits. |
| **Exports**             | \`export csv/json                                                  | 
| **Pluggable Storage**   | JSON by default; SQLite plugin for power-users.                    | 
| **100 % Test Coverage** | Every line & branch, enforced by CI.                               | 

<a id="install"></a>

## 3  Installation

```bash
pip install loopbloom-cli   # PyPI release
# or bleeding edge
pip install git+https://github.com/ashkuhlmann/loopbloom-cli.git@main
````

> **Requires** Python ≥ 3.9. Optional: `plyer` for desktop notifications.

<a id="quick-start"></a>

## 4  Quick Start

```bash
# 1  Create a goal area
loopbloom goal add "Sleep Hygiene"

# 2  Add a micro-habit (≤ 5 min!)
loopbloom micro add --goal "Sleep Hygiene" --name "Wake up at 08:00" \
                   --cue "After alarm" --scaffold "Alarm+Sunlight" --target-time 08:00

# 3  Begin tracking each day
loopbloom checkin --goal "Sleep Hygiene" --status done --note "Groggy but did it!"
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

$ loopbloom checkin --goal Exercise --status skip --note "Rainy" 
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
  loopbloom checkin   [--goal <name>] [--status done|skip] [--note ..]
  loopbloom summary   [--goal <name>]   # streak banner, next steps

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
    Progression -->|≥ 80 % / 14d| AdvanceBanner
    Progression -->|otherwise| CompassionateNudge
```

Parameters `threshold` and `window` are user-configurable.
When omitted by commands, the progression rule reads these values from
`~/.config/loopbloom/config.toml`.

<a id="notifications"></a>

## 11  Notifications

Terminal banners by default; desktop via `plyer` (`loopbloom config set notify desktop`).

<a id="export"></a>

## 12  Data Export

```bash
loopbloom export --fmt csv --out ~/Desktop/loopbloom_progress.csv
```

<a id="dev-guide"></a>

## 13  Developer Guide (Brief)

*Thin CLI → Service → Core → Storage* layered architecture; see [USER_GUIDE.md](USER_GUIDE.md) for full docs.

<a id="testing"></a>

## 14  Testing & CI

CI enforces a minimum of 80 % unit and integration test coverage.

<a id="contrib"></a>

## 15  Contributing

PRs welcome—see `CONTRIBUTING.md`.

<a id="changelog"></a>

## 16  Changelog

See [`CHANGELOG.md`](CHANGELOG.md).
