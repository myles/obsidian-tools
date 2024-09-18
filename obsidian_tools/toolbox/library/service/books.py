import logging
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
from fuzzywuzzy import process
import frontmatter
from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations import GoogleBooksClient, OpenLibraryClient
from obsidian_tools.toolbox.library.models import Book, Person
from obsidian_tools.utils.template import render_template

logger = logging.getLogger(__name__)


def ensure_required_books_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for books are set.
    """
    if config.BOOKS_DIR_PATH is None or config.BOOKS_DIR_PATH.exists() is False:
        raise ObsidianToolsConfigError("BOOKS_DIR_PATH")

    return True


def get_book_data_from_openlibrary(
    isbn: str,
    client: OpenLibraryClient,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Get the book data from Open Library.
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


def get_book_data_from_google_books(
    isbn: str,
    client: GoogleBooksClient,
) -> Union[Dict[str, Any], None]:
    """
    Get the book data from Google Books.
    """
    _, resp = client.get_book_by_isbn(isbn=isbn)
    data = resp.json()

    # Check the shape of the data.
    if data["totalItems"] == 0:
        return None
    elif data["totalItems"] > 1:
        logger.info(
            f"Multiple books found for ISBN {isbn}. Using the first one."
        )

    return data["items"][0]


def get_openlibrary_work_description(
    works_data: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Get the description from an Open Library work.

    - Grab the first work that has a description.
    - The descirption can be a string or a dictionary with a "value" key.
    """
    for work in works_data:
        if "description" not in work:
            continue

        description = work["description"]

        if isinstance(description, str):
            return description
        elif "value" in description:
            return description["value"]

    return None


def openlibrary_data_to_dataclass(
    book_data: Dict[str, Any],
    works_data: List[Dict[str, Any]],
    authors_data: List[Dict[str, Any]],
) -> Book:
    """
    Convert the Open Library book data to a Book dataclass.
    """
    # Get the description from the first work that has a description.
    description = get_openlibrary_work_description(works_data)

    # ISBN is not always present.
    isbn_13 = None
    if "isbn_13" in book_data and book_data["isbn_13"]:
        isbn_13 = book_data["isbn_13"][0]

    cover_url = f"https://covers.openlibrary.org/b/olid/{book_data['key'].replace('/books/', '')}-L.jpg"

    # Convert the authors to Person dataclasses.
    authors = [Person(name=author["name"]) for author in authors_data]

    return Book(
        title=book_data["title"],
        authors=authors,
        number_of_pages=book_data.get("number_of_pages") or None,
        description=description,
        isbn=isbn_13,
        cover_url=cover_url,
        openlibrary_book_id=book_data["key"].replace("/books/", ""),
    )


def google_books_data_to_dataclass(book_data: Dict[str, Any]) -> Book:
    """
    Convert the Google Books book data to a Book dataclass.
    """
    # Convert the authors to Person dataclasses.
    authors = [
        Person(name=author) for author in book_data["volumeInfo"]["authors"]
    ]

    # Google Books doesn't always have the number of pages.
    number_of_pages = None
    if "pageCount" in book_data["volumeInfo"]:
        number_of_pages = book_data["volumeInfo"]["pageCount"]

    # Google Books doesn't always have a description.
    description = None
    if "description" in book_data["volumeInfo"]:
        description = book_data["volumeInfo"]["description"]

    # Google Books doesn't always have the ISBN.
    isbn = None
    if "industryIdentifiers" in book_data["volumeInfo"]:
        isbn = next(
            filter(
                lambda x: x["type"] == "ISBN_13",
                book_data["volumeInfo"]["industryIdentifiers"],
            ),
            None,
        )
        if isbn:
            isbn = isbn["identifier"]

    # Google Books doesn't always have a cover URL.
    cover_url = None
    if (
        "imageLinks" in book_data["volumeInfo"]
        and "thumbnail" in book_data["volumeInfo"]["imageLinks"]
    ):
        cover_url = book_data["volumeInfo"]["imageLinks"]["thumbnail"]

    return Book(
        title=book_data["volumeInfo"]["title"],
        authors=authors,
        number_of_pages=number_of_pages,
        description=description,
        isbn=isbn,
        cover_url=cover_url,
        google_book_id=book_data["id"],
    )


def build_book_note(book: Book) -> str:
    """
    Build the note for a book.
    """
    content = render_template("library/book.md", book=book)
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


def load_book_note(file_path: Path) -> frontmatter.Post:
    """
    Load a book note.
    """
    with file_path.open("r") as file_obj:
        post = frontmatter.loads(file_obj.read())
    return post


def list_books_path(
    config: Config,
) -> Generator[Tuple[Path, frontmatter.Post], None, None]:
    """
    List the paths of book notes.
    """
    # This is just a sanity check. The ensure_required_books_config function
    # should catch this.
    if not config.BOOKS_DIR_PATH:
        raise ValueError(
            "BOOKS_DIR_PATH must be set in the configuration file."
        )

    for file_path in config.BOOKS_DIR_PATH.glob("*.md"):
        try:
            post = load_book_note(file_path)
        except FileNotFoundError:
            continue

        yield file_path, post


def search_books(
    search_term: str,
    books: List[Tuple[Path, frontmatter.Post]],
) -> List[Tuple[Path, frontmatter.Post]]:
    """
    Search the Obsidian vault for books.
    """
    return process.extract(
        query=search_term,
        choices=[str(post["title"]) for _path, post in books],
        limit=10,
    )
