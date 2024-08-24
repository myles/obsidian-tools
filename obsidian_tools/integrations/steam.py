from obsidian_tools.utils.http_client import HttpClient, RequestReturn
from requests.auth import AuthBase
from requests import PreparedRequest


class SteamClient(HttpClient):
    """
    A client for the Steam API.
    """

    def __init__(self, api_key: str, **kwargs):
        super().__init__(**kwargs)

        self.api_key = api_key

    def get_game(self, app_id: str) -> RequestReturn:
        """
        Get a game by its app ID.
        """
        return self.get(f"https://store.steampowered.com/api/appdetails", params={"appids": app_id})
