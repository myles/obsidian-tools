import pytest
import responses

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.tools.media import service


def test_ensure_required_config(vault_path):
    good_config = Config(
        VAULT_PATH=vault_path,
        MEDIA_DIR_PATH=vault_path / "media",
    )
    assert service.ensure_required_config(good_config) is True

    bad_config = Config(VAULT_PATH=vault_path)
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        service.ensure_required_config(bad_config)

    assert str(exc_info.value.config_key) == "MEDIA_DIR_PATH"


def test_ensure_required_books_config(vault_path):
    good_config = Config(
        VAULT_PATH=vault_path,
        BOOKS_DIR_PATH=vault_path / "media" / "books",
    )
    assert service.ensure_required_books_config(good_config) is True

    bad_config = Config(VAULT_PATH=vault_path)
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        service.ensure_required_books_config(bad_config)

    assert str(exc_info.value.config_key) == "BOOKS_DIR_PATH"


def test_ensure_required_tv_shows_config(vault_path):
    good_config = Config(
        VAULT_PATH=vault_path,
        TV_SHOWS_DIR_PATH=vault_path / "media" / "tv_shows",
        TMDB_API_KEY="i-am-a-tmdb-api-key",
    )
    assert service.ensure_required_tv_shows_config(good_config) is True

    bad_config = Config(
        VAULT_PATH=vault_path, TMDB_API_KEY="i-am-a-tmdb-api-key"
    )
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        service.ensure_required_tv_shows_config(bad_config)

    assert str(exc_info.value.config_key) == "TV_SHOWS_DIR_PATH"

    bad_config = Config(
        VAULT_PATH=vault_path,
        TV_SHOWS_DIR_PATH=vault_path / "media" / "tv_shows",
    )
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        service.ensure_required_tv_shows_config(bad_config)

    assert str(exc_info.value.config_key) == "TMDB_API_KEY"


@responses.activate
def test_get_book_data(
    resp_openlibrary_author,
    resp_openlibrary_author_two,
    resp_openlibrary_edition,
    resp_openlibrary_work,
):
    client = service.OpenLibraryClient()

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

    book, works, authors = service.get_book_data(isbn=isbn, client=client)

    assert book == resp_openlibrary_edition
    assert works == [resp_openlibrary_work]
    assert len(authors) == 2
    assert resp_openlibrary_author in authors
    assert resp_openlibrary_author_two in authors


@responses.activate
def test_get_tv_show_data(
    resp_tmdb_tv_series_details,
    resp_tmdb_tv_season_details,
):
    series_id = resp_tmdb_tv_series_details["id"]

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://api.themoviedb.org/3/tv/{series_id}",
            json=resp_tmdb_tv_series_details,
            status=200,
        )
    )

    for i in range(1, resp_tmdb_tv_series_details["number_of_seasons"] + 1):
        responses.add(
            responses.Response(
                method=responses.GET,
                url=f"https://api.themoviedb.org/3/tv/{series_id}/season/{i}",
                json=resp_tmdb_tv_season_details,
                status=200,
            )
        )

    client = service.TMDBClient(api_key="i-am-a-tmdb-api-key")

    tv_series, tv_seasons = service.get_tv_show_data(
        tv_series_id=series_id,
        client=client,
    )

    assert tv_series == resp_tmdb_tv_series_details
    assert len(tv_seasons) == resp_tmdb_tv_series_details["number_of_seasons"]
