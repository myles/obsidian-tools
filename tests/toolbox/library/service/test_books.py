from dataclasses import replace

import pytest
import responses

from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations.openlibrary import OpenLibraryClient
from obsidian_tools.toolbox.library.service import books


def test_ensure_required_books_config(mock_config):
    good_config = replace(
        mock_config,
        BOOKS_DIR_PATH=mock_config.VAULT_PATH / "library" / "books",
    )
    assert books.ensure_required_books_config(good_config) is True

    bad_config = replace(mock_config, BOOKS_DIR_PATH=None)
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        books.ensure_required_books_config(bad_config)

    assert str(exc_info.value.config_key) == "BOOKS_DIR_PATH"


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
