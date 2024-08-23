from pathlib import Path
from typing import Union

import click
import questionary

from obsidian_tools.config import Config
from obsidian_tools.integrations import (
    DiscogsClient,
    GoogleBooksClient,
    OpenLibraryClient,
    TMDBClient,
)
from obsidian_tools.toolbox.library.service import books, core, movies, tv_shows, vinyl
from obsidian_tools.utils.dataclasses import merge_dataclasses
from obsidian_tools.utils.decorators import write_option


@click.group()
@click.pass_context
def cli(ctx) -> None:
    """
    Tools for working with a digital library in an Obsidian vault.
    """
    config: Config = ctx.obj["config"]

    core.ensure_required_config(config)

    ctx.ensure_object(dict)

    # Open Library and Google Books do not require an API key.
    ctx.obj["openlibrary_client"] = OpenLibraryClient()
    ctx.obj["google_books_client"] = GoogleBooksClient()

    if config.TMDB_API_KEY is not None:
        ctx.obj["tmdb_client"] = TMDBClient(api_key=config.TMDB_API_KEY)

    if config.DISCOGS_PERSONAL_ACCESS_TOKEN is not None:
        ctx.obj["discogs_client"] = DiscogsClient(
            auth_token=config.DISCOGS_PERSONAL_ACCESS_TOKEN
        )

    return None


@cli.command()
@click.pass_context
@click.argument("isbn", type=str)
@write_option
def add_book(ctx: click.Context, isbn: str, write: bool) -> None:
    """
    Add a book to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    open_library_client: OpenLibraryClient = ctx.obj["openlibrary_client"]
    google_books_client: GoogleBooksClient = ctx.obj["google_books_client"]

    books.ensure_required_books_config(config)

    books_dir_path: Union[Path, None] = config.BOOKS_DIR_PATH
    if books_dir_path is None:
        raise Exception("BOOKS_DIR_PATH must be set in the configuration file.")

    open_library_book = books.openlibrary_book_data_to_dataclass(
        *books.get_book_data_from_openlibrary(
            isbn=isbn, client=open_library_client
        )
    )

    google_books_data = books.get_book_data_from_google_books(
        isbn=isbn, client=google_books_client
    )
    if google_books_data is not None:
        google_books_book = books.google_books_data_to_dataclass(
            google_books_data
        )
        book = merge_dataclasses(open_library_book, google_books_book)
    else:
        book = open_library_book

    note_content = books.build_book_note(book=book)
    if write is True:
        note_file_path = books.write_book_note(
            note_name=book.title,
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Book written to {note_file_path}")

    return click.echo(note_content)


@cli.command()
@click.pass_context
@write_option
def read_book(ctx: click.Context, write: bool) -> None:
    """
    Track reading a book in the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    books.ensure_required_books_config(config)

    book_note_paths = books.get_book_note_paths(config)
    selected_book_path = questionary.select(
        "Select a book",
        choices=[
            questionary.Choice(title=path.stem, value=path)
            for path in book_note_paths
        ],
    ).ask()

    breakpoint()
    return None


@cli.command()
@click.pass_context
@click.argument("tv_series_id", type=int)
@write_option
def add_tv_show(ctx: click.Context, tv_series_id: int, write: bool) -> None:
    """
    Add a TV show to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    client: TMDBClient = ctx.obj["tmdb_client"]

    tv_shows.ensure_required_tv_shows_config(config)

    tv_shows_dir_path: Union[Path, None] = config.TV_SHOWS_DIR_PATH
    if tv_shows_dir_path is None:
        raise Exception(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    tv_series, tv_seasons = tv_shows.get_tv_show_data(
        tv_series_id=tv_series_id,
        client=client,
    )

    note_name = tv_shows.build_tv_show_note_name(tv_series=tv_series)
    note_content = tv_shows.build_tv_show_note(
        tv_series=tv_series,
        tv_seasons=tv_seasons,
    )

    if write is True:
        note_path = tv_shows.build_tv_show_note_path(
            note_name=note_name, config=config
        )

        if note_path.exists() is True:
            existing_note = tv_shows.load_tv_show_note(note_path)

            if tv_shows.is_same_tv_show(tv_series, existing_note) is False:
                alt_note_names = tv_shows.list_alternative_note_names(
                    tv_series=tv_series, config=config
                )

                try:
                    selection = next(
                        filter(lambda x: x["is_same"], alt_note_names)
                    )
                    note_path = selection["path"]
                except StopIteration:
                    alt_note_name = questionary.select(
                        f"TV show note already exists at {note_path}. What would you like to do?",
                        choices=[
                            *[
                                questionary.Choice(
                                    title=alt_note_name["name"],
                                    value=alt_note_name["name"],
                                    disabled=(
                                        "already exists"
                                        if alt_note_name["does_exist"]
                                        else None
                                    ),
                                )
                                for alt_note_name in alt_note_names
                            ],
                            questionary.Separator(),
                            questionary.Choice(title="Overwrite"),
                        ],
                    ).ask()

                    if alt_note_name == "Overwrite":
                        click.confirm(
                            "Are you sure you want to overwrite the existing note?",
                            abort=True,
                        )
                    else:
                        note_path = tv_shows.build_tv_show_note_path(
                            note_name=alt_note_name, config=config
                        )

        note_file_path = tv_shows.write_tv_show_note(
            file_path=note_path,
            note_content=note_content,
            config=config,
        )

        return click.echo(f"TV show written to {note_file_path}")

    return click.echo(note_content)


@cli.command()
@click.pass_context
def update_tv_shows(ctx: click.Context) -> None:
    """
    Update TV show notes in the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    client: TMDBClient = ctx.obj["tmdb_client"]

    tv_shows.ensure_required_tv_shows_config(config)

    tv_shows_dir_path: Union[Path, None] = config.TV_SHOWS_DIR_PATH
    if tv_shows_dir_path is None:
        raise Exception(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    for path, post in tv_shows.list_tv_show_paths(config, has_tmdb_id=True):
        tv_series, tv_seasons = tv_shows.get_tv_show_data(
            tv_series_id=int(post["tmdb_id"]),
            client=client,
        )

        note_content = tv_shows.build_tv_show_note(
            tv_series=tv_series,
            tv_seasons=tv_seasons,
        )

        tv_shows.write_tv_show_note(
            file_path=path,
            note_content=note_content,
            config=config,
        )

        click.echo(f"Updated {path}")


@cli.command()
@click.pass_context
@click.argument("movie_id", type=int)
@write_option
def add_movie(ctx: click.Context, movie_id: int, write: bool) -> None:
    """
    Add a Movie to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    client: TMDBClient = ctx.obj["tmdb_client"]

    movies.ensure_required_movies_config(config)

    movies_dir_path: Union[Path, None] = config.MOVIES_DIR_PATH
    if movies_dir_path is None:
        raise Exception(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    movie = movies.get_movie_data(movie_id=movie_id, client=client)

    note_name = movie["title"]
    note_content = movies.build_movie_note(movie=movie)

    if write is True:
        note_file_path = movies.write_movie_note(
            note_name=note_name,
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Movie written to {note_file_path}")

    return click.echo(note_content)


@cli.command()
@click.pass_context
@click.argument("search_query", type=str, required=False)
@click.option("--isbn", type=str)
@click.option("--discogs-release-id", type=int)
@write_option
def add_vinyl(
    ctx: click.Context,
    search_query: Union[str, None],
    isbn: Union[str, None],
    discogs_release_id: Union[int, None],
    write: bool,
) -> None:
    """
    Add a vinyl record to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    client: DiscogsClient = ctx.obj["discogs_client"]

    movies.ensure_required_movies_config(config)

    # If no search query, barcode, or Discogs release ID is provided, prompt
    # the user for a search query.
    if search_query is None and isbn is None and discogs_release_id is None:
        search_query = click.prompt("Enter a search query")

    # If we have a search query or an ISBN, search for the vinyl release.
    if search_query is not None or isbn is not None:
        search_results = vinyl.search_vinyl_on_discogs(
            client=client,
            query=search_query,
            barcode=isbn,
        )

        releases = search_results["results"]
        discogs_release_id = questionary.select(
            "Which release?",
            choices=[
                questionary.Choice(title=release["title"], value=release["id"])
                for release in releases
            ],
        ).ask()

    if discogs_release_id is None:
        raise click.ClickException("Discogs release ID must be provided.")

    vinyl_record = vinyl.discogs_release_data_to_dataclass(
        vinyl.get_vinyl_data_from_discogs_release(
            discogs_release_id=discogs_release_id,
            client=client,
        )
    )

    note_name = vinyl_record.title
    if vinyl_record.artists:
        note_name += f" - {vinyl_record.display_artists}"

    note_content = vinyl.build_vinyl_note(vinyl_record=vinyl_record)

    if write is True:
        note_file_path = vinyl.write_vinyl_note(
            note_name=note_name,
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Vinyl record written to {note_file_path}")

    return click.echo(note_content)
