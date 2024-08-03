from pathlib import Path
from typing import Any, Dict, List, Tuple

from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.tools.media.clients.tmdb import TMDBClient
from obsidian_tools.utils.template import render_template


def ensure_required_config(config: Config) -> bool:
    """
    Ensure that the required configuration values are set.
    """
    if config.MEDIA_DIR_PATH is None or config.MEDIA_DIR_PATH.exists() is False:
        raise ObsidianToolsConfigError("MEDIA_DIR_PATH")

    return True


def ensure_required_tv_shows_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for TV shows are set.
    """
    if (
        config.TV_SHOWS_DIR_PATH is None
        or config.TV_SHOWS_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("TV_SHOWS_DIR_PATH")

    if not config.TMDB_API_KEY:
        raise ObsidianToolsConfigError("TMDB_API_KEY")

    return True


def get_tv_show_data(
    tv_series_id: int,
    client: TMDBClient,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Get the data for a TV show.
    """
    _, resp_tv_series = client.get_tv_series_details(series_id=tv_series_id)
    tv_series = resp_tv_series.json()

    tv_seasons = []
    for season_number in range(1, tv_series["number_of_seasons"] + 1):
        _, resp_tv_season = client.get_tv_season_details(
            series_id=tv_series["id"],
            season_number=season_number,
        )
        tv_season = resp_tv_season.json()
        tv_seasons.append(tv_season)

    return tv_series, tv_seasons


def build_tv_show_note(
    tv_series: Dict[str, Any],
    tv_seasons: List[Dict[str, Any]],
) -> str:
    """
    Build the note for a TV show.
    """
    content = render_template(
        "media/tv_show.md",
        tv_series=tv_series,
        tv_seasons=tv_seasons,
    )
    return content.strip()


def write_tv_show_note(
    note_name: str,
    note_content: str,
    config: Config,
) -> Path:
    """
    Write the note for a TV show.
    """
    # This is just a sanity check. The ensure_required_tv_shows_config function
    # should catch this.
    if not config.TV_SHOWS_DIR_PATH:
        raise ValueError(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    file_name = sanitize(note_name) + ".md"
    file_path = config.TV_SHOWS_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
