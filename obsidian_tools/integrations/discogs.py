from typing import Literal, Optional

from requests.auth import AuthBase

from obsidian_tools.utils.http_client import HttpClient, RequestReturn


class DiscogsAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["Authorization"] = f"Discogs token={self.token}"
        return r


class DiscogsClient(HttpClient):

    def __init__(self, auth_token: str, **kwargs):
        auth = DiscogsAuth(token=auth_token)
        super().__init__(auth=auth, **kwargs)

        self.base_url = "https://api.discogs.com"

    # Release
    def get_release(
        self,
        release_id: int,
        curr_abbr: Optional[
            Literal[
                "USD",
                "GBP",
                "EUR",
                "CAD",
                "AUD",
                "JPY",
                "CHF",
                "MXN",
                "BRL",
                "NZD",
                "SEK",
                "ZAR",
            ]
        ] = None,
        **kwargs,
    ) -> RequestReturn:
        """
        Get a Discogs release.
        """
        if "params" in kwargs:
            params = kwargs.pop("params")
        else:
            params = {}

        if curr_abbr is not None:
            params["curr_abbr"] = curr_abbr

        url = f"{self.base_url}/releases/{release_id}"
        request, response = self.get(url, params=params, **kwargs)
        response.raise_for_status()

        return request, response

    # Search
    def search(
        self,
        query: Optional[str] = None,
        barcode: Optional[str] = None,
        result_type: Optional[
            Literal["release", "master", "artist", "label"]
        ] = None,
        result_format: Optional[
            Literal["vinyl", "cd", "cassette", "dvd", "blu-ray", "other"]
        ] = None,
        **kwargs,
    ) -> RequestReturn:
        """
        Search the Discogs database.
        """
        if "params" in kwargs:
            params = kwargs.pop("params")
        else:
            params = {}

        if query is not None:
            params["q"] = query

        if barcode is not None:
            params["barcode"] = barcode

        if result_type is not None:
            params["type"] = result_type

        if result_format is not None:
            params["format"] = result_format

        url = f"{self.base_url}/database/search"
        request, response = self.get(url, params=params, **kwargs)
        response.raise_for_status()

        return request, response
