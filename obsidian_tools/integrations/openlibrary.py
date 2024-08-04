from typing import Generator, Iterable, Optional

from requests import Session

from obsidian_tools.utils.http_client import HttpClient, RequestReturn


class OpenLibraryClient(HttpClient):
    def __init__(self, session: Optional[Session] = None):
        super().__init__(session=session)

        self.base_url = "https://openlibrary.org"

    def get_book_from_isbn(self, isbn: str, **kwargs) -> RequestReturn:
        """
        Get a book from the OpenLibrary API using its ISBN.
        """
        url = f"{self.base_url}/isbn/{isbn}.json"

        request, response = self.get(url=url, **kwargs)
        response.raise_for_status()

        return request, response

    def get_author(self, key: str, **kwargs) -> RequestReturn:
        """
        Get an author from the OpenLibrary API using its key.
        """
        url = f"{self.base_url}/authors/{key}.json"

        request, response = self.get(url=url, **kwargs)
        response.raise_for_status()

        return request, response

    def get_authors(
        self, author_keys: Iterable[str], **kwargs
    ) -> Generator[RequestReturn, None, None]:
        """
        Get a list of authors from OpenLibrary API using their keys.
        """
        for author_key in author_keys:
            yield self.get_author(key=author_key, **kwargs)

    def get_work(self, key: str, **kwargs) -> RequestReturn:
        """
        Get a work from OpenLibrary API using its key.
        """
        url = f"{self.base_url}/works/{key}.json"

        request, response = self.get(url=url, **kwargs)
        response.raise_for_status()

        return request, response

    def get_works(
        self, work_keys: Iterable[str], **kwargs
    ) -> Generator[RequestReturn, None, None]:
        """
        Get a list of works from OpenLibrary API using their keys.
        """
        for work_key in work_keys:
            yield self.get_work(key=work_key, **kwargs)
