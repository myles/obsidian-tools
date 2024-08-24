from obsidian_tools.integrations import IGDBClient, SteamClient
from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from typing import Any, Dict, List, Tuple
from obsidian_tools.toolbox.library.models import VideoGame
from obsidian_tools.utils.template import render_template

from sanitize_filename import sanitize
from pathlib import Path


def ensure_required_video_game_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for video games are set.
    """
    if config.IGDB_CLIENT_ID is None:
        raise ObsidianToolsConfigError("IGDB_CLIENT_ID")

    if config.IGDB_CLIENT_SECRET is None:
        raise ObsidianToolsConfigError("IGDB_CLIENT_SECRET")

    return True


def search_video_game_on_igdb(
    client: IGDBClient,
    query: str,
) -> List[Dict[str, Any]]:
    """
    Search for a video game on IGDB.
    """
    request, response = client.search_games(query=query)
    return response.json()


def get_game_data_from_igdb(
    client: IGDBClient,
    game_id: int,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Get the data of a video game from IGDB.
    """
    _, resp_game = client.get_game(game_id=game_id)
    game = resp_game.json()[0]

    _, resp_cover = client.get_cover(cover_id=game["cover"])
    cover = resp_cover.json()[0]

    return game, cover


def igdb_data_to_dataclass(
    game: Dict[str, Any],
    cover: Dict[str, Any],
) -> VideoGame:
    """
    Convert an IGDB video game response to a dataclass.
    """
    return VideoGame(
        title=game["name"],
        description=game.get("summary"),
        cover_url=f"https://images.igdb.com/igdb/image/upload/t_cover_big/{cover['image_id']}.jpg",
        igdb_id=game["id"],
    )


def get_game_data_from_steam(
    client: SteamClient,
    app_id: str,
) -> Dict[str, Any]:
    """
    Get the data of a video game from Steam.
    """
    _, response = client.get_game(app_id=app_id)
    resp_json = response.json()

    if resp_json[app_id]["success"] is False:
        raise ValueError(f"Failed to get data for app ID {app_id}.")

    return resp_json[app_id]['data']


def steam_data_to_dataclass(
    game_data: Dict[str, Any],
) -> VideoGame:
    """
    Convert a Steam video game response to a dataclass.
    """
    return VideoGame(
        title=game_data["name"],
        description=game_data.get("short_description"),
        cover_url=game_data["header_image"],
        steam_id=game_data["steam_appid"],
    )


def build_video_game_note(video_game: VideoGame) -> str:
    """
    Build the note for a video game.
    """
    content = render_template("library/video_game.md", video_game=video_game)
    return content.strip()


def write_video_game(
    note_name: str,
    note_content: str,
    config: Config,
) -> Path:
    """
    Write the note for a video game.
    """
    # This is just a sanity check. The ensure_required_video_games_config
    # function should catch this.
    if not config.VIDEO_GAMES_DIR_PATH:
        raise ValueError(
            "VIDEO_GAMES_DIR_PATH must be set in the configuration file."
        )

    file_name = sanitize(note_name) + ".md"
    file_path = config.VIDEO_GAMES_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
