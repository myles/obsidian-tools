from pathlib import Path
from typing import Any, Dict, List, Tuple, TypedDict, Generator

import frontmatter
from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations import TMDBClient
from obsidian_tools.utils.humanize import and_join
from obsidian_tools.utils.template import render_template


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
        "library/tv_show.md",
        tv_series=tv_series,
        tv_seasons=tv_seasons,
    )
    return content.strip()


def build_tv_show_note_name(tv_series: Dict[str, Any]) -> str:
    """
    Build the name for a TV show note.
    """
    return f"{tv_series['name']}"


def is_same_tv_show(tv_series: Dict[str, Any], post: frontmatter.Post) -> bool:
    """
    Check if the TV show data matches the note data.
    """
    return tv_series["id"] == post["tmdb_id"]


def load_tv_show_note(file_path: Path) -> frontmatter.Post:
    """
    Load a TV show note.
    """
    with file_path.open("r") as file_obj:
        post = frontmatter.loads(file_obj.read())
    return post



class AltNoteName(TypedDict):

    name: str
    path: Path
    does_exist: bool
    is_same: bool


def list_alternative_note_names(
    tv_series: Dict[str, Any],
    config: Config,
) -> List[AltNoteName]:
    """
    List alternative note names for a TV show.
    """
    possible_note_names = [
        build_tv_show_note_name(tv_series),
        f"{tv_series['name']} ({tv_series['first_air_date'][:4]})",
        f"{tv_series['name']} ({and_join(tv_series['origin_country'])})",
    ]

    note_names = []
    for note_name in possible_note_names:
        note_path = build_tv_show_note_path(note_name, config)
        try:
            post = load_tv_show_note(note_path)
        except FileNotFoundError:
            post = None

        note_names.append(
            {
                "name": note_name,
                "path": note_path,
                "does_exist": note_path.exists(),
                "is_same": (
                    is_same_tv_show(tv_series, post)
                    if post is not None
                    else False
                ),
            }
        )

    return note_names


def build_tv_show_note_path(note_name: str, config: Config) -> Path:
    """
    Build the path for a TV show note.
    """
    file_name = sanitize(note_name) + ".md"
    return config.TV_SHOWS_DIR_PATH / file_name


def write_tv_show_note(
    file_path: Path,
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

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path


def list_tv_show_paths(
    config: Config,
    has_tmdb_id: bool = False,
) -> Generator[Tuple[Path, frontmatter.Post], None, None]:
    """
    List the paths of TV show notes.
    """
    for file_path in config.TV_SHOWS_DIR_PATH.glob("*.md"):
        try:
            post = load_tv_show_note(file_path)
        except FileNotFoundError:
            continue

        if has_tmdb_id and "tmdb_id" not in post:
            continue

        yield file_path, post
