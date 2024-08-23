import pytest
import responses
from dataclasses import replace
from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations.tmdb import TMDBClient
from obsidian_tools.toolbox.library.service import tv_shows


def test_ensure_required_tv_shows_config(mock_config):
    good_config = replace(
        mock_config,
        TV_SHOWS_DIR_PATH=mock_config.VAULT_PATH / "library" / "tv_shows",
        TMDB_API_KEY="i-am-a-tmdb-api-key",
    )
    assert tv_shows.ensure_required_tv_shows_config(good_config) is True

    bad_config = replace(
        mock_config, TMDB_API_KEY="i-am-a-tmdb-api-key"
    )
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        tv_shows.ensure_required_tv_shows_config(bad_config)

    assert str(exc_info.value.config_key) == "TV_SHOWS_DIR_PATH"

    bad_config = replace(
        mock_config,
        TV_SHOWS_DIR_PATH=mock_config.VAULT_PATH / "library" / "tv_shows",
    )
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        tv_shows.ensure_required_tv_shows_config(bad_config)

    assert str(exc_info.value.config_key) == "TMDB_API_KEY"


@responses.activate
def test_get_tv_show_data(
    resp_tmdb_tv_series_details,
    resp_tmdb_tv_season_details,
):
    series_id = resp_tmdb_tv_series_details["id"]

    responses.add(
        responses.Response(
            method=responses.GET,
            url=f"https://api.themoviedb.org/3/tv/{series_id}",
            json=resp_tmdb_tv_series_details,
            status=200,
        )
    )

    for i in range(1, resp_tmdb_tv_series_details["number_of_seasons"] + 1):
        responses.add(
            responses.Response(
                method=responses.GET,
                url=f"https://api.themoviedb.org/3/tv/{series_id}/season/{i}",
                json=resp_tmdb_tv_season_details,
                status=200,
            )
        )

    client = TMDBClient(api_key="i-am-a-tmdb-api-key")

    tv_series, tv_seasons = tv_shows.get_tv_show_data(
        tv_series_id=series_id,
        client=client,
    )

    assert tv_series == resp_tmdb_tv_series_details
    assert len(tv_seasons) == resp_tmdb_tv_series_details["number_of_seasons"]
