import responses

from obsidian_tools.integrations.openlibrary import OpenLibraryClient


@responses.activate
def test_openlibrary_client__get_book_from_isbn(resp_openlibrary_edition):
    client = OpenLibraryClient()

    isbn = "9780141182550"

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://openlibrary.org/isbn/{isbn}.json",
            json=resp_openlibrary_edition,
            status=200,
        )
    )

    request, response = client.get_book_from_isbn(isbn)
    assert response.status_code == 200
    assert response.json() == resp_openlibrary_edition


@responses.activate
def test_openlibrary_client__get_author(resp_openlibrary_author):
    client = OpenLibraryClient()

    author_key = resp_openlibrary_author["key"].replace("/authors/", "")

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://openlibrary.org/authors/{author_key}.json",
            json=resp_openlibrary_author,
            status=200,
        )
    )

    request, response = client.get_author(author_key)
    assert response.status_code == 200
    assert response.json() == resp_openlibrary_author


@responses.activate
def test_openlibrary_client__get_work(resp_openlibrary_work):
    client = OpenLibraryClient()

    work_key = resp_openlibrary_work["key"].replace("/works/", "")

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://openlibrary.org/works/{work_key}.json",
            json=resp_openlibrary_work,
            status=200,
        )
    )

    request, response = client.get_work(work_key)
    assert response.status_code == 200
    assert response.json() == resp_openlibrary_work
