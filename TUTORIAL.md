# Getting Started with LoopBloom

This short tutorial walks you through installing the CLI, adding your first goal, checking in, and viewing progress. Screenshots are taken from a typical terminal session; your prompts may look slightly different.

## 1. Installation

LoopBloom requires **Python 3.10 or later**. Install the package from PyPI:

```bash
pip install loopbloom-cli
```

Optional: `plyer` enables desktop notifications.

## 2. Create a Goal

A goal groups one or more micro-habits. Start by creating a goal area:

```bash
loopbloom goal add "Exercise"
```

You should see confirmation similar to:

```console
✓ Added goal: Exercise
```

## 3. Add a Micro-Habit

Next, define a small action that takes five minutes or less. The name is positional; add an optional goal (and phase if you want):

```bash
loopbloom micro add "Walk 5 min" --goal "Exercise"
```

The CLI replies with something like:

```console
✓ Micro-habit added: Walk 5 min
```

## 4. Check In Each Day

Record whether you completed the micro-habit:

```bash
loopbloom checkin Exercise --success --note "Sunny walk"
```

Sample output:

```console
✓ Logged!  🎉  Your consistency is paying off—great job showing up even when busy.
```

## 5. View Progress

Use the `summary` and `report` commands to track success rates and trends:

```bash
loopbloom summary
loopbloom report --mode calendar
```

Example summary banner:

```console
┏━━━━━━━━━━━━━━━━━━━━━━━ LoopBloom ━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Goal            Streak   Last 14 Days   Next Action       ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Exercise        ▇▇▇▇▇▇▇▇  8/14 (57 %)    Stay the course ✨ ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## 6. Explore Coping Plans

Coping plans provide guided prompts when you're feeling stuck.

```bash
loopbloom cope list          # show available plans
loopbloom cope run overwhelm # step through a plan
```

Running a plan presents a series of questions to help you refocus. Create your own with `loopbloom cope new`.

---

You're now ready to continue building habits with LoopBloom. For more details see [`USER_GUIDE.md`](USER_GUIDE.md).
