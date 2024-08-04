from pathlib import Path
from typing import Any, Dict, List, Tuple

from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations.openlibrary import OpenLibraryClient
from obsidian_tools.utils.template import render_template


def ensure_required_books_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for books are set.
    """
    if config.BOOKS_DIR_PATH is None or config.BOOKS_DIR_PATH.exists() is False:
        raise ObsidianToolsConfigError("BOOKS_DIR_PATH")

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
    work_keys = [work["key"].replace("/works/", "") for work in book["works"]]

    works = []
    for _, resp_work in client.get_works(work_keys=work_keys):
        work = resp_work.json()
        works.append(work)

        author_keys.extend(
            [
                author["author"]["key"].replace("/authors/", "")
                for author in work["authors"]
            ]
        )

    authors = []
    for _, resp_author in client.get_authors(author_keys=set(author_keys)):
        authors.append(resp_author.json())

    return book, works, authors


def build_book_note(
    book: Dict[str, Any],
    works: List[Dict[str, Any]],
    authors: List[Dict[str, Any]],
) -> str:
    """
    Build the note for a book.
    """
    content = render_template(
        "library/book.md", book=book, works=works, authors=authors
    )
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
        raise ValueError(
            "BOOKS_DIR_PATH must be set in the configuration file."
        )

    file_name = sanitize(note_name) + ".md"
    file_path = config.BOOKS_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
