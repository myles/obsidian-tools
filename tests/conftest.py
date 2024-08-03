import json
from pathlib import Path

import pytest

EXAMPLE_DIR_PATH = Path(__file__).parent / "example"
RESPONSES_DIR_PATH = Path(__file__).parent / "responses"


@pytest.fixture
def vault_path():
    return EXAMPLE_DIR_PATH / "vault"


@pytest.fixture
def resp_tmdb_tv_episode_details():
    path_obj = RESPONSES_DIR_PATH / "tmdb" / "tv-episode-details.json"
    with path_obj.open() as file_obj:
        return json.load(file_obj)


@pytest.fixture
def resp_tmdb_tv_season_details():
    path_obj = RESPONSES_DIR_PATH / "tmdb" / "tv-season-details.json"
    with path_obj.open() as file_obj:
        return json.load(file_obj)


@pytest.fixture
def resp_tmdb_tv_series_details():
    path_obj = RESPONSES_DIR_PATH / "tmdb" / "tv-series-details.json"
    with path_obj.open() as file_obj:
        return json.load(file_obj)
