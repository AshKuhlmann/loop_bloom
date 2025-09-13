"""Goal hierarchy tree command.

Renders all goals, phases and micro-habits in a nested tree using Rich's
``Tree`` class for a pleasant overview.
"""

from typing import List

import click
from rich.tree import Tree

from loopbloom.cli import ui, with_goals
from loopbloom.core.models import GoalArea

console = ui.console


@click.command(name="tree", help="Show goal hierarchy as a tree.")
@with_goals
def tree(goals: List[GoalArea]) -> None:
    """Display all goals, phases, and micro-habits in a tree view."""
    # Start with a single root node. The tree emoji helps users quickly locate
    # this view in their terminal history.
    root = Tree("\U0001f333 LoopBloom Goals")
    for g in goals:
        g_branch = root.add(g.name)
        # Show micro-habits grouped by phase to mirror the goal hierarchy.
        for ph in g.phases:
            p_branch = g_branch.add(f"[dim]Phase:[/] {ph.name}")
            for m in ph.micro_goals:
                p_branch.add(m.name)
        # Also include any micro-habits that aren't part of a phase so nothing
        # is missed.
        for m in g.micro_goals:
            g_branch.add(m.name)
    console.print(root)


tree_cmd = tree
