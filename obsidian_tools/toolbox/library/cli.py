from pathlib import Path
from typing import Union

import click

from obsidian_tools.config import Config
from obsidian_tools.integrations.openlibrary import OpenLibraryClient
from obsidian_tools.integrations.tmdb import TMDBClient
from obsidian_tools.toolbox.library.service import books, core, tv_shows


@click.group()
@click.pass_context
def cli(ctx):
    """
    Tools for working with a digital library in an Obsidian vault.
    """
    config: Config = ctx.obj["config"]

    core.ensure_required_config(config)

    ctx.ensure_object(dict)

    # Google Books doesn't require an API key.
    ctx.obj["openlibrary_client"] = OpenLibraryClient()

    if config.TMDB_API_KEY is not None:
        ctx.obj["tmdb_client"] = TMDBClient(api_key=config.TMDB_API_KEY)


@cli.command()
@click.pass_context
@click.argument("isbn", type=str)
@click.option(
    "-w",
    "--write",
    is_flag=True,
    help="Write the file to the vault.",
)
def add_book(ctx: click.Context, isbn: str, write: bool):
    """
    Add a book to the Obsidian vault.
    """
    books.ensure_required_books_config(ctx.obj["config"])

    client: OpenLibraryClient = ctx.obj["openlibrary_client"]
    config: Config = ctx.obj["config"]

    books_dir_path: Union[Path, None] = config.BOOKS_DIR_PATH

    if books_dir_path is None:
        raise click.ClickException(
            "BOOKS_DIR_PATH must be set in the configuration file."
        )

    book, works, authors = books.get_book_data(isbn=isbn, client=client)

    note_content = books.build_book_note(
        book=book, works=works, authors=authors
    )

    if write is True:
        note_file_path = books.write_book_note(
            note_name=book["title"],
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Book written to {note_file_path}")

    click.echo(note_content)


@cli.command()
@click.pass_context
@click.argument("tv_series_id", type=int)
@click.option(
    "-w",
    "--write",
    is_flag=True,
    help="Write the file to the vault.",
)
def add_tv_show(ctx: click.Context, tv_series_id: int, write: bool):
    """
    Add a TV show to the Obsidian vault.
    """
    tv_shows.ensure_required_tv_shows_config(ctx.obj["config"])

    client: TMDBClient = ctx.obj["tmdb_client"]
    config: Config = ctx.obj["config"]

    tv_shows_dir_path: Union[Path, None] = config.TV_SHOWS_DIR_PATH

    if tv_shows_dir_path is None:
        raise click.ClickException(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    tv_series, tv_seasons = tv_shows.get_tv_show_data(
        tv_series_id=tv_series_id,
        client=client,
    )

    note_content = tv_shows.build_tv_show_note(
        tv_series=tv_series,
        tv_seasons=tv_seasons,
    )

    if write is True:
        note_file_path = tv_shows.write_tv_show_note(
            note_name=tv_series["name"],
            note_content=note_content,
            config=config,
        )
        return click.echo(f"TV show written to {note_file_path}")

    click.echo(note_content)
