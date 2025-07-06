from datetime import date, timedelta

import click

from loopbloom.core import config as cfg

_DEF_HELP = "Pause notifications globally or for a specific goal."


def _parse_duration(text: str) -> timedelta | None:
    text = text.strip().lower()
    if not text:
        return None
    num = "".join(ch for ch in text if ch.isdigit())
    unit = text[len(num) :]
    if not num or unit not in {"d", "w"}:
        return None
    days = int(num) * (7 if unit == "w" else 1)
    return timedelta(days=days)


@click.command(name="pause", help=_DEF_HELP)
@click.option("--goal", "goal_name", default=None, help="Pause a single goal.")
@click.option(
    "--for",
    "duration",
    required=True,
    help="Pause length (1w or 3d)",
)
def pause(goal_name: str | None, duration: str) -> None:
    """Pause notifications for ``duration`` days or weeks."""
    delta = _parse_duration(duration)
    if not delta:
        raise click.BadParameter(
            "Invalid duration format. Use Nd or Nw e.g. 3d, 1w",
            param_hint="--for",
        )
    until = (date.today() + delta).isoformat()
    conf = cfg.load()
    if goal_name:
        pauses = conf.get("goal_pauses", {})
        pauses[goal_name] = until
        conf["goal_pauses"] = pauses
        click.echo(f"[green]Paused '{goal_name}' until {until}.")
    else:
        conf["pause_until"] = until
        click.echo(f"[green]Paused all notifications until {until}.")
    cfg.save(conf)


pause_cmd = pause
