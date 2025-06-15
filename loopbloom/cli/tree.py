"""Goal hierarchy tree command."""

from typing import List

import click
from rich.console import Console
from rich.tree import Tree

from loopbloom.cli import with_goals
from loopbloom.core.models import GoalArea

console = Console()


@click.command(name="tree", help="Show goal hierarchy as a tree.")
@with_goals
def tree(goals: List[GoalArea]) -> None:
    """Display all goals, phases, and micro-habits in a tree view."""
    root = Tree("\U0001F333 LoopBloom Goals")
    for g in goals:
        g_branch = root.add(g.name)
        # Add micro-goals in phases
        for ph in g.phases:
            p_branch = g_branch.add(f"[dim]Phase:[/] {ph.name}")
            for m in ph.micro_goals:
                p_branch.add(m.name)
        # Add direct micro-goals
        for m in g.micro_goals:
            g_branch.add(m.name)
    console.print(root)
