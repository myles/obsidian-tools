from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple, TypedDict, Union

import frontmatter
from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations import IGDBClient, SteamClient
from obsidian_tools.integrations.igdb import CategoryEnum
from obsidian_tools.toolbox.library.models import VideoGame
from obsidian_tools.utils.template import render_template


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
    game_id: Union[str, int],
) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
    """
    Get the data of a video game from IGDB.
    """
    _, resp_game = client.get_game(game_id=game_id)
    game = resp_game.json()[0]

    _, resp_cover = client.get_cover(cover_id=game["cover"])
    cover = resp_cover.json()[0]

    _, resp_external_games = client.get_external_game(
        external_game_ids=game["external_games"]
    )
    external_games = resp_external_games.json()

    return game, cover, external_games


def get_igdb_game_id_from_external_game_id(
    client: IGDBClient,
    external_game_id: str,
    category: CategoryEnum,
) -> str:
    """
    Get the IGDB game ID from an external game ID.
    """
    _, response = client.get_game_by_external_game_id(
        game_id=external_game_id,
        category=category,
    )
    return response.json()[0]["id"]


def get_external_game_for_category(
    external_games: List[Dict[str, Any]],
    category: CategoryEnum,
) -> Union[None, Dict[str, Any]]:
    """
    Get the external game data for a specific category.
    """
    for external_game in external_games:
        if str(external_game["category"]) == str(category.value):
            return external_game

    return None


def igdb_data_to_dataclass(
    game: Dict[str, Any],
    cover: Dict[str, Any],
    external_games: List[Dict[str, Any]],
) -> VideoGame:
    """
    Convert an IGDB video game response to a dataclass.
    """
    steam_external_game = get_external_game_for_category(
        external_games, CategoryEnum.STEAM
    )

    steam_id = None
    if steam_external_game is not None:
        steam_id = steam_external_game["uid"]

    first_release_date = None
    if game["first_release_date"]:
        first_release_date = datetime.fromtimestamp(
            game["first_release_date"]
        ).date()

    return VideoGame(
        title=game["name"],
        description=game.get("summary"),
        cover_url=f"https://images.igdb.com/igdb/image/upload/t_cover_big/{cover['image_id']}.jpg",
        first_release_date=first_release_date,
        igdb_id=game["id"],
        steam_id=steam_id,
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

    return resp_json[app_id]["data"]


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


def build_video_game_note_name(video_game: VideoGame) -> str:
    """
    Build the name for a video game note.
    """
    return video_game.title


def build_video_game_note(video_game: VideoGame) -> str:
    """
    Build the note for a video game.
    """
    content = render_template("library/video_game.md", video_game=video_game)
    return content.strip()


def build_video_game_note_path(note_name: str, config: Config) -> Path:
    """
    Build the path for a video game note.
    """
    if not config.VIDEO_GAMES_DIR_PATH:
        raise ValueError(
            "VIDEO_GAMES_DIR_PATH must be set in the configuration file."
        )

    file_name = sanitize(note_name) + ".md"
    return config.VIDEO_GAMES_DIR_PATH / file_name


def write_video_game(
    note_path: Path,
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

    with note_path.open("w") as file_obj:
        file_obj.write(note_content)

    return note_path


def load_video_game(note_path: Path) -> frontmatter.Post:
    """
    Load a Movie note.
    """
    with note_path.open("r") as file_obj:
        post = frontmatter.load(file_obj)
    return post


def is_same_video_game(video_game: VideoGame, post: frontmatter.Post) -> bool:
    """
    Check if the Movie and the Post are the same.
    """
    if (
        video_game.igdb_id is not None
        and "igdb_id" in post
        and str(video_game.igdb_id) == str(post["igdb_id"])
    ):
        return True

    if (
        video_game.steam_id is not None
        and "steam_id" in post
        and str(video_game.steam_id) == str(post["steam_id"])
    ):
        return True

    return False


class AltNoteName(TypedDict):

    name: str
    path: Path
    does_exist: bool
    is_same: bool


def list_alternative_note_names(
    video_game: VideoGame,
    config: Config,
) -> List[AltNoteName]:
    """
    List the alternative note names for a Video Game.
    """
    possible_names = [build_video_game_note_name(video_game)]

    if video_game.first_release_date is not None:
        possible_names.append(
            f"{video_game.title} ({video_game.first_release_date.year})"
        )

    names = []
    for name in possible_names:
        path = build_video_game_note_path(name, config=config)
        try:
            post = load_video_game(path)
        except FileNotFoundError:
            post = None

        alt_name: AltNoteName = {
            "name": name,
            "path": path,
            "does_exist": path.exists(),
            "is_same": (
                is_same_video_game(video_game, post)
                if post is not None
                else False
            ),
        }
        names.append(alt_name)

    return names
