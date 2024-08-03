import logging
from obsidian_tools.utils.http_client import HttpClient


logger = logging.getLogger(__name__)


class GoogleBooksClient(HttpClient):
    """
    A client for the Google Books API.
    """

    def __init__(self):
        super().__init__()
        self.base_url = "https://www.googleapis.com/books/v1"

    def get_book_by_isbn(self, isbn: str):
        """
        Get a book from the Google Books API using its ISBN.
        """
        request, response = self.get(
            f"{self.base_url}/volumes", params={"q": f"isbn:{isbn}"}
        )
        response.raise_for_status()
        return request, response
