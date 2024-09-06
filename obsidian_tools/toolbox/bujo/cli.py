import datetime

import click

from obsidian_tools.config import Config
from obsidian_tools.toolbox.bujo.service import create, base
from obsidian_tools.utils.click_utils import (
    WeekFormat,
    write_force_option,
    write_option,
)
from obsidian_tools.utils.clock import get_start_of_week


@click.group()
@click.pass_context
def cli(ctx) -> None:
    """
    Tools for managing a Bullet Journal in Obsidian.
    """
    config: Config = ctx.obj["config"]

    base.ensure_required_config(config)

    ctx.ensure_object(dict)

    return None


@cli.command()
@click.pass_context
@click.argument("month", type=click.DateTime(formats=["%Y-%m"]))
@write_option
@write_force_option
def add_monthly(
    ctx: click.Context,
    month: datetime.datetime,
    write: bool,
    force: bool,
) -> None:
    """
    Add a new Monthly Note.
    """
    config: Config = ctx.obj["config"]

    note_content = create.build_monthly_log_note(date=month, config=config)

    if write is True:
        note_file_path = base.get_monthly_log_file_path(
            date=month, config=config
        )

        if note_file_path.exists() and force is False:
            click.echo(
                f"File already exists: {note_file_path}. Use --force if you want to overwrite the file."
            )
            return None

        create.write_log_note(note_file_path, note_content)
        click.echo(f"Monthly Log Note written to: {note_file_path}")
        return None

    click.echo(note_content)


@cli.command()
@click.pass_context
@click.argument("week", type=WeekFormat())
@write_option
@write_force_option
def add_weekly(
    ctx: click.Context,
    week: datetime.datetime,
    write: bool,
    force: bool,
) -> None:
    """
    Add a new Weekly Note.
    """
    config: Config = ctx.obj["config"]

    start_of_week = get_start_of_week(week)

    note_content = create.build_weekly_log_note(
        date=start_of_week, config=config
    )

    if write is True:
        note_file_path = base.get_weekly_log_file_path(
            date=start_of_week, config=config
        )

        if note_file_path.exists() and force is False:
            click.echo(
                f"File already exists: {note_file_path}. Use --force if you want to overwrite the file."
            )
            return None

        create.write_log_note(note_file_path, note_content)
        click.echo(f"Weekly Log Note written to: {note_file_path}")
        return None

    click.echo(note_content)
