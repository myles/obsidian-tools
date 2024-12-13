from pathlib import Path
from typing import Union

import click
import questionary
from requests import HTTPError, Timeout

from obsidian_tools.config import Config
from obsidian_tools.integrations import (
    DiscogsClient,
    GoogleBooksClient,
    IGDBClient,
    OpenLibraryClient,
    SteamClient,
    TMDBClient,
)
from obsidian_tools.integrations.igdb import CategoryEnum as IGDBCategoryEnum
from obsidian_tools.toolbox.library.models import Book
from obsidian_tools.toolbox.library.service import (
    books,
    core,
    movies,
    tv_shows,
    video_games,
    vinyl_records,
)
from obsidian_tools.utils.click_utils import write_force_option, write_option
from obsidian_tools.utils.dataclasses import merge_dataclasses


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

    if (
        config.IGDB_CLIENT_ID is not None
        and config.IGDB_CLIENT_SECRET is not None
    ):
        ctx.obj["igdb_client"] = IGDBClient(
            client_id=config.IGDB_CLIENT_ID,
            client_secret=config.IGDB_CLIENT_SECRET,
        )

    if config.STEAM_WEB_API_KEY is not None:
        ctx.obj["steam_client"] = SteamClient(api_key=config.STEAM_WEB_API_KEY)

    return None


@cli.command()
@click.pass_context
@click.argument("isbn", type=str)
@write_option
@write_force_option
def add_book(ctx: click.Context, isbn: str, write: bool, force: bool) -> None:
    """
    Add a book to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    open_library_client: OpenLibraryClient = ctx.obj["openlibrary_client"]
    google_books_client: GoogleBooksClient = ctx.obj["google_books_client"]

    books.ensure_required_books_config(config, write)

    # Attempt to get the book's data from Open Library and Google Books.
    ol_book: Union[Book, None] = None
    gb_book: Union[Book, None] = None

    try:
        ol_book_data, ol_works_data, ol_authors_data = (
            books.get_book_data_from_openlibrary(
                isbn=isbn, client=open_library_client
            )
        )
        ol_book = books.openlibrary_data_to_dataclass(
            book_data=ol_book_data,
            works_data=ol_works_data,
            authors_data=ol_authors_data,
        )
    except Timeout:
        click.echo("Open Library request timed out.", err=True)
    except HTTPError as http_error:
        if http_error.response.status_code != 404:
            raise http_error

        click.echo("Book not found on Open Library.", err=True)

    try:
        gb_book_data = books.get_book_data_from_google_books(
            isbn=isbn, client=google_books_client
        )
        if gb_book_data is not None:
            gb_book = books.google_books_data_to_dataclass(gb_book_data)
    except Timeout:
        click.echo("Google Books request timed out.", err=True)
    except HTTPError as http_error:
        if http_error.response.status_code != 404:
            raise http_error

        click.echo("Book not found on Google Books.", err=True)

    # If no book data is found, raise an exception.
    if gb_book is None and ol_book is None:
        raise click.ClickException("No book data found.")

    # Merge the book data from Open Library and Google Books or use the data
    # from one of the sources if the other is not available.
    if gb_book is not None and ol_book is not None:
        book = merge_dataclasses(ol_book, gb_book)
    else:
        book = ol_book or gb_book

    note_name = books.build_book_note_name(book=book)
    note_content = books.build_book_note(book=book)

    if write is True:
        note_path = books.build_book_note_path(
            note_name=note_name, config=config
        )

        if note_path.exists() is True and force is False:
            click.confirm(
                f"Note already exists at {note_path}. Overwrite?",
                abort=True,
            )

        note_file_path = books.write_book_note(
            note_path=note_path,
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Book written to {note_file_path}")

    return click.echo(note_content)


@cli.command()
@click.pass_context
@click.argument("search_query", type=str, required=False)
@click.option("--tmdb-id", type=int)
@write_option
def add_tv_show(
    ctx: click.Context,
    search_query: Union[str, None],
    tmdb_id: Union[int, None],
    write: bool = False,
) -> None:
    """
    Add a TV show to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    client: TMDBClient = ctx.obj["tmdb_client"]

    tv_shows.ensure_required_tv_shows_config(config, write)

    if search_query is None and tmdb_id is None:
        search_query = click.prompt("Enter a search query")

    if search_query is not None or tmdb_id is not None:
        search_results = tv_shows.search_tv_series_on_tmdb(
            client=client,
            query=search_query or "",
        )
        tmdb_id = questionary.select(
            "Which TV show?",
            choices=[
                questionary.Choice(
                    title=f"{tv_show['name']} ({tv_show['first_air_date']})",
                    value=tv_show["id"],
                )
                for tv_show in search_results
            ],
        ).ask()

    if tmdb_id is None:
        raise click.ClickException("TMDB ID must be provided.")

    tv_show = tv_shows.tmdb_tv_show_data_to_dataclasses(
        *tv_shows.get_tv_show_data_from_tmdb(
            tv_series_id=tmdb_id,
            client=client,
        )
    )

    note_name = tv_shows.build_tv_show_note_name(tv_show)
    note_content = tv_shows.build_tv_show_note(tv_show)

    if write is True:
        note_path = tv_shows.build_tv_show_note_path(
            note_name=note_name, config=config
        )

        if note_path.exists() is True:
            existing_note = tv_shows.load_tv_show_note(note_path)

            if tv_shows.is_same_tv_show(tv_show, existing_note) is False:
                alt_note_names = tv_shows.list_alternative_note_names(
                    tv_show, config=config
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

    tv_shows.ensure_required_tv_shows_config(config, write=True)

    for path, post in tv_shows.list_tv_show_paths(config, has_tmdb_id=True):
        tv_series_data_from_tmdb, tv_seasons_data_from_tmdb = (
            tv_shows.get_tv_show_data_from_tmdb(
                tv_series_id=int(post["tmdb_id"]),
                client=client,
            )
        )
        tv_show = tv_shows.tmdb_tv_show_data_to_dataclasses(
            tv_series=tv_series_data_from_tmdb,
            tv_seasons=tv_seasons_data_from_tmdb,
        )

        note_content = tv_shows.build_tv_show_note(tv_show)

        tv_shows.write_tv_show_note(
            file_path=path,
            note_content=note_content,
            config=config,
        )

        click.echo(f"Updated {path}")


@cli.command()
@click.pass_context
@click.argument("search_query", type=str, required=False)
@click.option("--tmdb-id", type=int)
@write_option
def add_movie(
    ctx: click.Context,
    search_query: Union[str, None],
    tmdb_id: Union[int, None],
    write: bool = False,
) -> None:
    """
    Add a Movie to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    client: TMDBClient = ctx.obj["tmdb_client"]

    movies.ensure_required_movies_config(config=config, write=write)

    # If no search query or TMDB ID is provided, prompt the user for a search
    # query.
    if search_query is None and tmdb_id is None:
        search_query = click.prompt("Enter a search query")

    if search_query is not None or tmdb_id is not None:
        search_results = movies.search_movies_on_tmdb(
            client=client,
            query=search_query or "",
        )
        tmdb_id = questionary.select(
            "Which movie?",
            choices=[
                questionary.Choice(
                    title=f"{movie['title']} ({movie['release_date']})",
                    value=movie["id"],
                )
                for movie in search_results
            ],
        ).ask()

    movies_dir_path: Union[Path, None] = config.MOVIES_DIR_PATH
    if write is True and movies_dir_path is None:
        raise Exception(
            "MOVIES_DIR_PATH must be set in the configuration file."
        )

    if tmdb_id is None:
        raise click.ClickException("TMDB ID must be provided.")

    movie = movies.tmdb_move_data_to_movie(
        movies.get_movie_data_from_tmdb(movie_id=tmdb_id, client=client)
    )

    note_name = movies.build_movie_note_name(movie=movie)
    note_content = movies.build_movie_note(movie=movie)

    if write is True:
        note_path = movies.build_movie_note_path(
            note_name=note_name, config=config
        )

        if note_path.exists() is True:
            existing_note = movies.load_movie_note(note_path)

            if movies.is_same_movie(movie, existing_note) is False:
                alt_note_names = movies.list_alternative_note_names(
                    movie, config=config
                )
                try:
                    selection = next(
                        filter(lambda x: x["is_same"], alt_note_names)
                    )
                    note_path = selection["path"]
                except StopIteration:
                    alt_note_name = questionary.select(
                        f"Movie note already exists at {note_path}. What would you like to do?",
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
                        note_path = movies.build_movie_note_path(
                            note_name=alt_note_name, config=config
                        )

        movies.write_movie_note(
            note_path=note_path,
            note_content=note_content,
            config=config,
        )

        return click.echo(f"Movie written to {note_path}")

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

    movies.ensure_required_movies_config(config, write=write)

    # If no search query, barcode, or Discogs release ID is provided, prompt
    # the user for a search query.
    if search_query is None and isbn is None and discogs_release_id is None:
        search_query = click.prompt("Enter a search query")

    # If we have a search query or an ISBN, search for the vinyl release.
    if search_query is not None or isbn is not None:
        search_results = vinyl_records.search_vinyl_on_discogs(
            client=client,
            query=search_query,
            barcode=isbn,
        )

        releases = search_results["results"]
        discogs_release_id = questionary.select(
            "Which release?",
            choices=[
                questionary.Choice(
                    title=f"{release['id']} — {release['title']}",
                    value=release["id"],
                )
                for release in releases
            ],
        ).ask()

    if discogs_release_id is None:
        raise click.ClickException("Discogs release ID must be provided.")

    vinyl_record = vinyl_records.discogs_release_data_to_dataclass(
        vinyl_records.get_vinyl_data_from_discogs_release(
            discogs_release_id=discogs_release_id,
            client=client,
        )
    )

    note_name = vinyl_record.title
    if vinyl_record.artists:
        note_name += f" - {vinyl_record.display_artists}"

    note_content = vinyl_records.build_vinyl_note(vinyl_record=vinyl_record)

    if write is True:
        note_file_path = vinyl_records.write_vinyl_note(
            note_name=note_name,
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Vinyl record written to {note_file_path}")

    return click.echo(note_content)


@cli.command()
@click.pass_context
@click.argument("search_query", type=str, required=False)
@click.option("--igdb-id", type=int)
@click.option("--steam-id", type=str)
@write_option
@write_force_option
def add_video_game(
    ctx: click.Context,
    search_query: Union[str, None],
    igdb_id: Union[int, None],
    steam_id: Union[str, None],
    write: bool,
    force: bool,
) -> None:
    """
    Add a video game to the Obsidian vault.
    """
    config: Config = ctx.obj["config"]
    igdb_client: IGDBClient = ctx.obj["igdb_client"]
    steam_client: SteamClient = ctx.obj["steam_client"]

    video_games.ensure_required_video_game_config(config)

    # If not search query, IGDB ID, or Steam ID is provided, prompt the user
    # for a search query.
    if search_query is None and igdb_id is None and steam_id is None:
        search_query = click.prompt("Enter a search query")

    # If we have a search query, search for the video game.
    if search_query is not None:
        search_results = video_games.search_video_game_on_igdb(
            client=igdb_client,
            query=search_query,
        )

        igdb_id = questionary.select(
            "Which game?",
            choices=[
                questionary.Choice(title=game["name"], value=game["id"])
                for game in search_results
            ],
        ).ask()

    if igdb_id is not None:
        video_game = video_games.igdb_data_to_dataclass(
            *video_games.get_game_data_from_igdb(
                client=igdb_client, game_id=igdb_id
            )
        )
    elif steam_id is not None:
        steam_video_game = video_games.steam_data_to_dataclass(
            video_games.get_game_data_from_steam(
                client=steam_client, app_id=steam_id
            )
        )
        igdb_game_id = video_games.get_igdb_game_id_from_external_game_id(
            client=igdb_client,
            external_game_id=steam_id,
            category=IGDBCategoryEnum.STEAM,
        )
        igdb_video_game = video_games.igdb_data_to_dataclass(
            *video_games.get_game_data_from_igdb(
                client=igdb_client, game_id=igdb_game_id
            )
        )
        video_game = merge_dataclasses(igdb_video_game, steam_video_game)
    else:
        raise click.ClickException("IGDB ID or Steam ID must be provided.")

    note_name = video_game.title
    note_content = video_games.build_video_game_note(
        video_game=video_game,
    )

    if write is True:
        note_path = video_games.build_video_game_note_path(
            note_name=note_name,
            config=config,
        )

        if note_path.exists() is True:
            existing_note = video_games.load_video_game(note_path)

            if (
                video_games.is_same_video_game(video_game, existing_note)
                is False
            ):
                alt_note_names = video_games.list_alternative_note_names(
                    video_game, config=config
                )
                try:
                    selection = next(
                        filter(lambda x: x["is_same"], alt_note_names)
                    )
                    note_path = selection["path"]
                except StopIteration:
                    alt_note_name = questionary.select(
                        f"Video game note already exists at {note_path}. What would you like to do?",
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
                        note_path = video_games.build_video_game_note_path(
                            note_name=alt_note_name, config=config
                        )

        video_games.write_video_game(
            note_path=note_path,
            note_content=note_content,
            config=config,
        )
        return click.echo(f"Video game written to {note_path}")

    return click.echo(note_content)
