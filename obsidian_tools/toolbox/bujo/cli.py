import click
from typing import Union
from obsidian_tools.config import Config
from obsidian_tools.toolbox.bujo import service
import datetime


@click.group()
@click.pass_context
def cli(ctx):
    """
    Tools for working with a digital library in an Obsidian vault.
    """
    config: Config = ctx.obj["config"]

    service.ensure_required_config(config)

    ctx.ensure_object(dict)


@cli.command()
@click.pass_context
@click.option('-m', '--month', help='The month to build the log for, in the format YYYY-MM.')
@click.option(
    "-w",
    "--write",
    is_flag=True,
    help="Write the file to the vault.",
)
def monthly_log(ctx, month: Union[str, None], write: bool = False):
    """
    Build the monthly log for the current or given month.
    """
    config: Config = ctx.obj["config"]

    service.ensure_required_config(config)

    if month is None:
        date = datetime.date.today()
    else:
        date = datetime.datetime.strptime(month, "%Y-%m").date()

    note_content = service.build_monthly_log_note(
        service.get_monthly_log_context(date)
    )

    if write is True:
        note_file_path = service.write_monthly_log_note(
            note_name=service.build_monthly_log_file_name(date, config),
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Note written to: {note_file_path}")

    click.echo(note_content)
