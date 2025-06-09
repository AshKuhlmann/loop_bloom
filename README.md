# MicroHabits CLI 🧩

*Compassion‑first habit‑building for ADHD brains and anyone who prefers **tiny, sustainable wins** over motivational hype.*

<p align="center">
  <!-- Badges (replace links before release) -->
  <img src="https://img.shields.io/badge/build-passing-green" alt="Build Status" />
  <img src="https://img.shields.io/badge/coverage-100%25-brightgreen" alt="Coverage" />
  <img src="https://img.shields.io/pypi/v/microhabits-cli" alt="PyPI" />
  <img src="https://img.shields.io/github/license/ashkuhlmann/microhabits-cli" alt="License" />
</p>

> **TL;DR**
> • Install once → pick goals → forget the spreadsheets.
> • Define *micro‑habits* that take ≤ 5 min.
> • Log progress with a single command.
> • The CLI talks *to you* (self‑talk & encouragement), not the other way around.
> • When you achieve **≥ 80 % success over 14 days**, it nudges you to level‑up—gently.

---

## Table of Contents

1. [Why MicroHabits CLI?](#why)
2. [Feature Highlights](#features)
3. [Installation](#install)
4. [Quick Start](#quick-start)
5. [Sample Session](#sample)
6. [Command Cheatsheet](#cheatsheet)
7. [Configuration](#config)
8. [Storage Back‑Ends](#storage)
9. [Coping Plans](#coping)
10. [Progression Engine](#progression)
11. [Notifications](#notifications)
12. [Data Export](#export)
13. [Developer Guide](#dev-guide)
14. [Testing & CI](#testing)
15. [Contributing](#contrib)
16. [Changelog](#changelog)
17. [License](#license)

---

<a id="why"></a>

## 1  Why MicroHabits CLI?

Traditional trackers assume unlimited will‑power and demand elaborate setups. **MicroHabits CLI** is designed to be a **"set‑and‑forget" personal trainer**:

* **Zero spreadsheet anxiety** – one command creates goals; the app tracks everything.
* **Strategic Effort > Endless Will‑power** – focus on one doable habit at a time.
* **Self‑talk for you** – the tool generates compassionate, upbeat messages so you don’t have to.
* **Slips ≠ Failure** – built‑in self‑compassion and fast re‑engagement.
* **Invisible Scaffolding** – cues, streak banners, notifications, and coping guides.

<a id="features"></a>

## 2  Feature Highlights

| Area                    | What you get                                                       |                                      |
| ----------------------- | ------------------------------------------------------------------ | ------------------------------------ |
| **Hierarchical Goals**  | `goal → phase → micro` with reorder, cancel, edit.                 |                                      |
| **Fast Check‑ins**      | `checkin` records ✓/✕ & note in <10 s—CLI responds with self‑talk. |                                      |
| **Smart Progression**   | ≥ 80 % over 14 days triggers *advance* prompt.                     |                                      |
| **Guided Coping**       | `cope` launches YAML Q\&A scripts for overwhelm.                   |                                      |
| **Gentle Banners**      | `summary` prints streaks, nudges, celebrations. Optional `--goal`. |                                      |
| **Exports**             | \`export csv                                                       | json\` for spreadsheets or BI tools. |
| **Pluggable Storage**   | JSON by default; SQLite plugin for power‑users.                    |                                      |
| **100 % Test Coverage** | Every line & branch, enforced by CI.                               |                                      |

<a id="install"></a>

## 3  Installation

```bash
pip install microhabits-cli   # PyPI release
# or bleeding edge
pip install git+https://github.com/ashkuhlmann/microhabits-cli.git@main
```

> **Requires** Python ≥ 3.9. Optional: `plyer` for desktop notifications.

<a id="quick-start"></a>

## 4  Quick Start

```bash
# 1  Create a goal area
micro goal add "Sleep Hygiene"

# 2  Add a micro‑habit (≤ 5 min!)
micro micro add --goal "Sleep Hygiene" --name "Wake up at 08:00" \
                 --cue "After alarm" --scaffold "Alarm+Sunlight" --target-time 08:00

# 3  Begin tracking each day
micro checkin --goal "Sleep Hygiene" --status done --note "Groggy but did it!"
```

The CLI replies with something like:

```
✓ Logged!  🎉  Your consistency is paying off—great job showing up even when groggy.
```

<a id="sample"></a>

## 5  Sample Session

<details>
<summary>Click to expand</summary>

```console
$ micro summary
┏━━━━━━━━━━━━━━━━━━━━━━━ MicroHabits ━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Goal            Streak   Last 14 Days   Next Action       ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Sleep Hygiene   ▇▇▇▇▇▇▇▇  10/14 (71 %)   Stay the course ✨ ┃
┃ Exercise        ▇▇▇▁▇▇▇▇  12/14 (86 %)   Advance? (type Y) ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
Tip: `micro summary --goal "Exercise"` for details.

$ micro summary --goal "Exercise"
Goal: Exercise → Micro #1 "Walk 5 min"
• Success rate: 86 % (last 14 days)
• Auto‑advance suggestion: ➜ "Walk 6 min"  (accept? [Y/n])

$ micro checkin --goal Exercise --status skip --note "Rainy" 
⚠️  Skipped today. Mini‑pep‑talk: “A single rainy day doesn’t wash away progress—see you tomorrow!”

$ micro cope run overwhelmed
👉  Identify the biggest stressor right now:  _inbox backlog_
👉  Pick one micro‑action that would lighten it by 1 %:  _triage 5 emails_
💬  Great job—action dispels anxiety. 💪
```

</details>

<a id="cheatsheet"></a>

## 6  Command Cheatsheet

```text
micro help                         # global help

GOALS & MICRO‑HABITS
  micro goal  list|add|edit|rm                # manage goal areas
  micro phase list|add|edit|rm                # optional phases
  micro micro list|add|edit|rm|start|cancel   # micro‑habit operations

CHECK‑INS & FEEDBACK
  micro checkin   [--goal <name>] [--status done|skip] [--note ..]
  micro summary   [--goal <name>]   # streak banner, next steps

COPING & SUPPORT
  micro cope list           # view plan names
  micro cope run <name>     # guided coping walkthrough

DATA & CONFIG
  micro export --fmt csv|json --out progress.csv
  micro config set key val | get key | view
```

<a id="config"></a>

## 7  Configuration

Settings live in `~/.config/microhabits/config.toml` (XDG). Example:

```toml
storage = "json"            # json | sqlite
notify  = "terminal"        # terminal | desktop | none
advance.threshold = 0.80    # float (0‑1)
advance.window    = 14       # days
```

CLI shortcut: `micro config set storage sqlite`.

<a id="storage"></a>

## 8  Storage Back‑Ends

| Backend                                                              | Path                       | Use‑case                             |
| -------------------------------------------------------------------- | -------------------------- | ------------------------------------ |
| **JSON** (default)                                                   | `~/.microhabits/data.json` | Simple, git‑friendly.                |
| **SQLite**                                                           | `~/.microhabits/data.db`   | Large histories, multi‑tool queries. |
| Custom stores implement the `Storage` protocol in `storage/base.py`. |                            |                                      |

<a id="coping"></a>

## 9  Coping Plans

Coping scripts live in `microhabits/data/*.yml`; they drive `micro cope run <name>`.

<a id="progression"></a>

## 10  Progression Engine

```mermaid
flowchart TD
    Checkin -- emits --> EventBus
    EventBus --> Progression[progression.eval()]
    Progression -->|≥ 80 % / 14d| AdvanceBanner
    Progression -->|otherwise| CompassionateNudge
```

Parameters `threshold` and `window` are user‑configurable.

<a id="notifications"></a>

## 11  Notifications

Terminal banners by default; desktop via `plyer` (`micro config set notify desktop`).

<a id="export"></a>

## 12  Data Export

```bash
micro export --fmt csv --out ~/Desktop/microhabits_progress.csv
```

<a id="dev-guide"></a>

## 13  Developer Guide (Brief)

*Thin CLI → Service → Core → Storage* layered architecture; see `USER_GUIDE.md` for full docs.

<a id="testing"></a>

## 14  Testing & CI

100 % unit & integration coverage enforced in CI.

<a id="contrib"></a>

## 15  Contributing

PRs welcome—see `CONTRIBUTING.md`.

<a id="changelog"></a>

## 16  Changelog

See [`CHANGELOG.md`](CHANGELOG.md).

<a id="license"></a>

## 17  License

MIT © Ash Kuhlmann
