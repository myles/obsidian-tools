from pathlib import Path
from typing import Any, Dict, List, Tuple
import logging
from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError, ObsidianToolsError
from obsidian_tools.tools.media.clients.tmdb import TMDBClient
from obsidian_tools.tools.media.clients.openlibrary import OpenLibraryClient
from obsidian_tools.utils.template import render_template


logger = logging.getLogger(__name__)


def ensure_required_config(config: Config) -> bool:
    """
    Ensure that the required configuration values are set.
    """
    if config.MEDIA_DIR_PATH is None or config.MEDIA_DIR_PATH.exists() is False:
        raise ObsidianToolsConfigError("MEDIA_DIR_PATH")

    return True


def ensure_required_books_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for books are set.
    """
    if (
        config.BOOKS_DIR_PATH is None
        or config.BOOKS_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("BOOKS_DIR_PATH")

    return True


def ensure_required_tv_shows_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for TV shows are set.
    """
    if (
        config.TV_SHOWS_DIR_PATH is None
        or config.TV_SHOWS_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("TV_SHOWS_DIR_PATH")

    if not config.TMDB_API_KEY:
        raise ObsidianToolsConfigError("TMDB_API_KEY")

    return True


def get_book_data(
    isbn: str,
    client: OpenLibraryClient,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Get the data for a book.
    """
    _, resp_book = client.get_book_from_isbn(isbn=isbn)
    book = resp_book.json()

    author_keys = []
    work_keys = [work['key'].replace('/works/', '') for work in book["works"]]

    works = []
    for _, resp_work in client.get_works(work_keys=work_keys):
        work = resp_work.json()
        works.append(work)

        author_keys.extend([author['author']['key'].replace('/authors/', '') for author in work['authors']])

    authors = []
    for _, resp_author in client.get_authors(author_keys=set(author_keys)):
        authors.append(resp_author.json())

    return book, works, authors


def build_book_note(book: Dict[str, Any], works: List[Dict[str, Any]], authors: List[Dict[str, Any]]) -> str:
    """
    Build the note for a book.
    """
    content = render_template("media/book.md", book=book, works=works, authors=authors)
    return content.strip()


def write_book_note(
    note_name: str,
    note_content: str,
    config: Config,
) -> Path:
    """
    Write the note for a book.
    """
    # This is just a sanity check. The ensure_required_books_config function
    # should catch this.
    if not config.BOOKS_DIR_PATH:
        raise ValueError("BOOKS_DIR_PATH must be set in the configuration file.")

    file_name = sanitize(note_name) + ".md"
    file_path = config.BOOKS_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path


def get_tv_show_data(
    tv_series_id: int,
    client: TMDBClient,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Get the data for a TV show.
    """
    _, resp_tv_series = client.get_tv_series_details(series_id=tv_series_id)
    tv_series = resp_tv_series.json()

    tv_seasons = []
    for season_number in range(1, tv_series["number_of_seasons"] + 1):
        _, resp_tv_season = client.get_tv_season_details(
            series_id=tv_series["id"],
            season_number=season_number,
        )
        tv_season = resp_tv_season.json()
        tv_seasons.append(tv_season)

    return tv_series, tv_seasons


def build_tv_show_note(
    tv_series: Dict[str, Any],
    tv_seasons: List[Dict[str, Any]],
) -> str:
    """
    Build the note for a TV show.
    """
    content = render_template(
        "media/tv_show.md",
        tv_series=tv_series,
        tv_seasons=tv_seasons,
    )
    return content.strip()


def write_tv_show_note(
    note_name: str,
    note_content: str,
    config: Config,
) -> Path:
    """
    Write the note for a TV show.
    """
    # This is just a sanity check. The ensure_required_tv_shows_config function
    # should catch this.
    if not config.TV_SHOWS_DIR_PATH:
        raise ValueError(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    file_name = sanitize(note_name) + ".md"
    file_path = config.TV_SHOWS_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
