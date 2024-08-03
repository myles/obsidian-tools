from enum import Enum
from importlib.metadata import version
from typing import Dict, Optional, Tuple

from requests import PreparedRequest, Request, Response, Session
from requests.auth import AuthBase

RequestReturn = Tuple[PreparedRequest, Response]


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"
    PUT = "PUT"


class HttpClient:
    def __init__(
        self,
        session: Optional[Session] = None,
        auth: Optional[AuthBase] = None,
    ):
        if session is None:
            self.session = Session()
        else:
            self.session = session

        # Set the authentication method if provided.
        if auth is not None:
            self.session.auth = auth

        # Set a custom User-Agent header because we are nice web citizens.
        user_agent = f"obsidian-tools/{version('obsidian-tools')} (+https://github.com/myles/obsidian-tools/)"
        self.session.headers.update({"User-Agent": user_agent})

    def request(
        self,
        method: HttpMethod,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> RequestReturn:
        request = Request(
            method=str(method.value),
            url=url,
            headers=headers,
            params=params,
            **kwargs,
        )
        prepare_request = self.session.prepare_request(request)
        response = self.session.send(prepare_request, stream=stream)
        return prepare_request, response

    def get(self, url: str, **kwargs) -> RequestReturn:
        return self.request(HttpMethod.GET, url, **kwargs)
