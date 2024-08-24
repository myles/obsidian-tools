from typing import Optional

from requests.auth import AuthBase

from obsidian_tools.utils.http_client import HttpClient, RequestReturn


class TMDBAuth(AuthBase):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def __call__(self, request):
        request.headers["Authorization"] = f"Bearer {self.api_key}"
        return request


class TMDBClient(HttpClient):
    """
    A client for The Movie Database (TMDb) API.
    """

    def __init__(
        self, api_key: str, api_version: int = 3, **kwargs
    ):
        auth = TMDBAuth(api_key=api_key)
        super().__init__(auth=auth, **kwargs)

        self.base_url = f"https://api.themoviedb.org/{api_version}"

    # Movies
    def get_movie_details(self, movie_id: int) -> RequestReturn:
        """
        Get the details of a movie.

        - Docs: https://developer.themoviedb.org/reference/movie-details
        """
        url = f"{self.base_url}/movie/{movie_id}"

        request, response = self.get(url)
        response.raise_for_status()

        return request, response

    # TV Series
    def get_tv_series_details(self, series_id: int) -> RequestReturn:
        """
        Get the details of a TV series.

        - Docs: https://developer.themoviedb.org/reference/tv-series-details
        """
        url = f"{self.base_url}/tv/{series_id}"

        request, response = self.get(url)
        response.raise_for_status()

        return request, response

    # TV Seasons
    def get_tv_season_details(
        self, series_id: int, season_number: int
    ) -> RequestReturn:
        """
        Get the details of a TV season.

        - Docs: https://developer.themoviedb.org/reference/tv-season-details
        """
        url = f"{self.base_url}/tv/{series_id}/season/{season_number}"

        request, response = self.get(url)
        response.raise_for_status()

        return request, response

    # TV Episodes
    def get_tv_episode_details(
        self, series_id: int, season_number: int, episode_number: int
    ) -> RequestReturn:
        """
        Get the details of a TV episode.

        - Docs: https://developer.themoviedb.org/reference/tv-episode-details
        """
        url = f"{self.base_url}/tv/{series_id}/season/{season_number}/episode/{episode_number}"

        request, response = self.get(url)
        response.raise_for_status()

        return request, response
