import responses
from responses.matchers import query_param_matcher

from obsidian_tools.integrations.google_books import GoogleBooksClient


@responses.activate
def test_google_books_client__get_book_by_isbn(resp_google_books_volumes):
    client = GoogleBooksClient()

    isbn = next(
        filter(
            lambda x: x["type"] == "ISBN_13",
            resp_google_books_volumes["items"][0]["volumeInfo"][
                "industryIdentifiers"
            ],
        )
    )["identifier"]

    responses.add(
        responses.Response(
            method=responses.GET,
            url="https://www.googleapis.com/books/v1/volumes",
            json=resp_google_books_volumes,
            status=200,
            match=[query_param_matcher({"q": f"isbn:{isbn}"})],
        )
    )

    request, response = client.get_book_by_isbn(isbn)
    assert response.status_code == 200
    assert response.json() == resp_google_books_volumes
