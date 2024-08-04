from obsidian_tools.utils.http_client import HttpClient, RequestReturn


class GoogleBooksClient(HttpClient):
    """
    A client for the Google Books API.
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.googleapis.com/books/v1"

    def get_book_by_isbn(self, isbn: str) -> RequestReturn:
        """
        Get a book from the Google Books API using its ISBN.
        """
        request, response = self.get(
            f"{self.base_url}/volumes", params={"q": f"isbn%3A{isbn}"}
        )
        response.raise_for_status()
        return request, response
