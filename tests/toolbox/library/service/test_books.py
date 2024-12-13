from dataclasses import replace

import pytest
import responses

from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations.openlibrary import OpenLibraryClient
from obsidian_tools.toolbox.library.models import Book, Person
from obsidian_tools.toolbox.library.service import books


def test_ensure_required_books_config(mock_config):
    config = replace(
        mock_config,
        BOOKS_DIR_PATH=mock_config.VAULT_PATH / "library" / "books",
    )
    result = books.ensure_required_books_config(config, write=True)
    assert result is True

    config_without_book_dir_path = replace(mock_config, BOOKS_DIR_PATH=None)
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        books.ensure_required_books_config(config_without_book_dir_path, write=True)

    assert str(exc_info.value.config_key) == "BOOKS_DIR_PATH"

    result = books.ensure_required_books_config(config, write=False)
    assert result is True


@responses.activate
def test_get_book_data_from_openlibrary(
    resp_openlibrary_author,
    resp_openlibrary_author_two,
    resp_openlibrary_edition,
    resp_openlibrary_work,
):
    client = OpenLibraryClient()

    isbn = resp_openlibrary_edition["isbn_13"][0]
    author_one_key = resp_openlibrary_author["key"].replace("/authors/", "")
    author_two_key = resp_openlibrary_author_two["key"].replace("/authors/", "")
    work_key = resp_openlibrary_work["key"].replace("/works/", "")

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://openlibrary.org/isbn/{isbn}.json",
            json=resp_openlibrary_edition,
            status=200,
        )
    )
    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://openlibrary.org/authors/{author_one_key}.json",
            json=resp_openlibrary_author,
            status=200,
        )
    )
    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://openlibrary.org/authors/{author_two_key}.json",
            json=resp_openlibrary_author_two,
            status=200,
        )
    )
    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://openlibrary.org/works/{work_key}.json",
            json=resp_openlibrary_work,
            status=200,
        )
    )

    book, works, authors = books.get_book_data_from_openlibrary(
        isbn=isbn, client=client
    )

    assert book == resp_openlibrary_edition
    assert works == [resp_openlibrary_work]
    assert len(authors) == 2
    assert resp_openlibrary_author in authors
    assert resp_openlibrary_author_two in authors


def test_build_book_note():
    book = Book(title="A Game of Thrones")

    content = books.build_book_note(book)

    assert (
        content
        == f"""---
title: {book.title}
type: Book
aliases:
- {book.title}
---"""
    )


def test_build_book_note__everything():
    author = Person(name="George R.R. Martin")
    book = Book(
        title="A Game of Thrones",
        authors=[author],
        number_of_pages=694,
        description="A Game of Thrones is the first novel in A Song of Ice and Fire, a series of fantasy novels by American author George R. R. Martin.",
        isbn="9780553103540",
        cover_url="https://example.com/book_jacket.jpg",
        google_book_id="B_qNEAAAQBAJ",
        openlibrary_book_id="OL26425339M",
    )

    content = books.build_book_note(book)
    assert (
        content
        == f"""---
title: {book.title}
type: Book
aliases:
- {book.title}
authors: {book.display_authors}
number_of_pages: {book.number_of_pages}
isbn_13: '{book.isbn}'
google_book_id: {book.google_book_id}
openlibrary_book_id: {book.openlibrary_book_id}
---

![{book.title}]({book.cover_url})

{book.description}"""
    )
