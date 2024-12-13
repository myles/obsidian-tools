from enum import Enum
from typing import Iterable

from requests import Session
from requests.auth import AuthBase

from obsidian_tools.utils.http_client import HttpClient, RequestReturn


class CategoryEnum(Enum):
    STEAM = 1
    GOG = 5
    YOUTUBE = 10
    MICROSOFT = 11
    APPLE = 13
    TWITCH = 14
    ANDROID = 15
    AMAZON_ASIN = 20
    AMAZON_LUNA = 22
    AMAZON_ADG = 23
    EPIC_GAME_STORE = 26
    OCULUS = 28
    UTOMIK = 29
    ITCH_IO = 30
    XBOX_MARKETPLACE = 31
    KARTRIDGE = 32
    PLAYSTATION_STORE_US = 36
    FOCUS_ENTERTAINMENT = 37
    XBOX_GAME_PASS_ULTIMATE_CLOUD = 54
    GAMEJOLT = 55


class MediaEnum(Enum):
    DIGITAL = 1
    PHYSICAL = 2


class IGDBAuth(AuthBase):
    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id
        self.access_token = access_token

    def __call__(self, request):
        request.headers["Client-ID"] = self.client_id
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        return request


class IGDBClient(HttpClient):
    """
    A client for the IGDB API.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_version: int = 4,
        **kwargs,
    ):
        self.session = Session()

        # Authenticate with the IGDB API.
        _, auth_resp = self.authenticate(
            client_id=client_id, client_secret=client_secret
        )
        access_token = auth_resp.json()["access_token"]

        auth = IGDBAuth(client_id=client_id, access_token=access_token)
        super().__init__(session=self.session, auth=auth)

        self.base_url = f"https://api.igdb.com/v{api_version}"

    def authenticate(self, client_id: str, client_secret: str) -> RequestReturn:
        """
        Authenticate with the IGDB API.
        """
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        request, response = self.post(
            "https://id.twitch.tv/oauth2/token", data=data
        )
        response.raise_for_status()

        return request, response

    def search_games(self, query: str) -> RequestReturn:
        """
        Search for games on IGDB.
        """
        url = f"{self.base_url}/games"
        data = f'fields *; search "{query}";'

        request, response = self.post(url, data=data)
        response.raise_for_status()

        return request, response

    def get_game(self, game_id: int) -> RequestReturn:
        """
        Get the details of a game.
        """
        url = f"{self.base_url}/games"
        data = f"fields *; where id = {game_id};"

        request, response = self.post(url, data=data)
        response.raise_for_status()

        return request, response

    def get_game_by_external_game_id(
        self, game_id: str, category: CategoryEnum
    ) -> RequestReturn:
        """
        Get the details of a game by its external game ID.
        """
        url = f"{self.base_url}/games"
        data = f'fields *; where external_games.category = {category.value} & external_games.uid = "{game_id}";'

        request, response = self.post(url, data=data)
        response.raise_for_status()

        return request, response

    def get_cover(self, cover_id: int) -> RequestReturn:
        """
        Get the cover of a game.
        """
        url = f"{self.base_url}/covers"
        data = f"fields *; where id = {cover_id};"

        request, response = self.post(url, data=data)
        response.raise_for_status()

        return request, response

    def get_external_game(
        self, external_game_ids: Iterable[int]
    ) -> RequestReturn:
        """
        Get the external game data.
        """
        url = f"{self.base_url}/external_games"
        data = f"fields *; where id = ({','.join(str(i) for i in external_game_ids)});"

        request, response = self.post(url, data=data)
        response.raise_for_status()

        return request, response
