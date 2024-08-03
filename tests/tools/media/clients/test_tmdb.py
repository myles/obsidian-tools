import responses
from requests import Request

from obsidian_tools.tools.media.clients.tmdb import TMDBAuth, TMDBClient


def test_tmdb_auth():
    api_key = "i-am-a-tmdb-api-key"
    expected_authorization_header = f"Bearer {api_key}"

    auth = TMDBAuth(api_key=api_key)
    request = Request("GET", "https://example.com")
    request = auth(request)

    assert request.headers["Authorization"] == expected_authorization_header


@responses.activate
def test_tmdb_client__get_tv_series_details(resp_tmdb_tv_series_details):
    series_id = resp_tmdb_tv_series_details["id"]

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://api.themoviedb.org/3/tv/{series_id}",
            json=resp_tmdb_tv_series_details,
            status=200,
        )
    )

    client = TMDBClient(api_key="i-am-a-tmdb-api-key")
    request, response = client.get_tv_series_details(series_id=series_id)

    assert response.status_code == 200
    assert response.json() == resp_tmdb_tv_series_details


@responses.activate
def test_tmdb_client__get_tv_season_details(resp_tmdb_tv_season_details):
    series_id = resp_tmdb_tv_season_details["id"]
    season_number = resp_tmdb_tv_season_details["season_number"]

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://api.themoviedb.org/3/tv/{series_id}/season/{season_number}",
            json=resp_tmdb_tv_season_details,
            status=200,
        )
    )

    client = TMDBClient(api_key="i-am-a-tmdb-api-key")
    request, response = client.get_tv_season_details(
        series_id=series_id, season_number=season_number
    )

    assert response.status_code == 200
    assert response.json() == resp_tmdb_tv_season_details


@responses.activate
def test_tmdb_client__get_tv_episode_details(resp_tmdb_tv_episode_details):
    series_id = resp_tmdb_tv_episode_details["id"]
    season_number = resp_tmdb_tv_episode_details["season_number"]
    episode_number = resp_tmdb_tv_episode_details["episode_number"]

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://api.themoviedb.org/3/tv/{series_id}/season/{season_number}/episode/{episode_number}",
            json=resp_tmdb_tv_episode_details,
            status=200,
        )
    )

    client = TMDBClient(api_key="i-am-a-tmdb-api-key")
    request, response = client.get_tv_episode_details(
        series_id=series_id,
        season_number=season_number,
        episode_number=episode_number,
    )

    assert response.status_code == 200
    assert response.json() == resp_tmdb_tv_episode_details
