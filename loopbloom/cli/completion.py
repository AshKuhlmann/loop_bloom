"""Shell completion script generator.

Provides a `loopbloom completion [bash|zsh|fish|pwsh]` command that prints
the appropriate completion script to stdout. Users can eval or install the
output per their shell.
"""

from __future__ import annotations

import os
from typing import Literal, Optional, cast

import click

from loopbloom.cli import ui

console = ui.console


def _detect_shell() -> Literal["bash", "zsh", "fish", "pwsh"]:
    shell_env = os.getenv("SHELL", "").lower()
    if shell_env.endswith("zsh"):
        return "zsh"
    if shell_env.endswith("fish"):
        return "fish"
    if shell_env.endswith("powershell") or shell_env.endswith("pwsh"):
        return "pwsh"
    return "bash"


def _script_for(shell: Literal["bash", "zsh", "fish", "pwsh"]) -> str:
    prog = "loopbloom"
    env_name = "_LOOPBLOOM_COMPLETE"
    if shell == "bash":
        return 'eval "$(%s=bash_source %s)"\n' % (env_name, prog)
    if shell == "zsh":
        return 'eval "$(%s=zsh_source %s)"\n' % (env_name, prog)
    if shell == "fish":
        return "eval (env %s=fish_source %s)\n" % (env_name, prog)
    # PowerShell / pwsh
    # Use the simple on-demand registration approach compatible with Click.
    return (
        "$Env:%s = 'powershell'; "
        "%s | Out-String | Invoke-Expression; "
        "Remove-Item Env:%s\n" % (env_name, prog, env_name)
    )


@click.command(name="completion", help="Print shell completion script.")
@click.argument(
    "shell",
    required=False,
    type=click.Choice(["bash", "zsh", "fish", "pwsh"], case_sensitive=False),
)
def completion(shell: Optional[str]) -> None:
    """Print a shell completion script for the selected shell.

    If no shell is specified, an attempt is made to detect it from $SHELL.
    """
    sh = cast(
        Literal["bash", "zsh", "fish", "pwsh"], (shell or _detect_shell()).lower()
    )
    script = _script_for(sh)
    console.print(script, end="")


completion_cmd = completion
