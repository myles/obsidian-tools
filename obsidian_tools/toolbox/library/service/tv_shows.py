import datetime
import typing as t
from pathlib import Path

import frontmatter
from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations import TMDBClient
from obsidian_tools.toolbox.library import models
from obsidian_tools.utils.humanize import and_join
from obsidian_tools.utils.template import render_template


def ensure_required_tv_shows_config(config: Config, write: bool) -> bool:
    """
    Ensure that the required configuration values for TV shows are set.
    """
    if write is True and (
        config.TV_SHOWS_DIR_PATH is None
        or config.TV_SHOWS_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("TV_SHOWS_DIR_PATH")

    if not config.TMDB_API_KEY:
        raise ObsidianToolsConfigError("TMDB_API_KEY")

    return True


def search_tv_series_on_tmdb(
    client: TMDBClient, query: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Search for a tv-series on TMDB.
    """
    _, resp_movies = client.search_tv_series(query=query)
    return resp_movies.json()["results"]


def get_tv_show_season_data_from_tmdb(
    tv_series_id: int,
    season_number: int,
    client: TMDBClient,
) -> t.Dict[str, t.Any]:
    """
    Get the data for a TV show season.
    """
    _, resp_tv_season = client.get_tv_season_details(
        series_id=tv_series_id,
        season_number=season_number,
    )
    tv_season = resp_tv_season.json()
    return tv_season


def get_tv_show_data_from_tmdb(
    tv_series_id: int,
    client: TMDBClient,
) -> t.Tuple[t.Dict[str, t.Any], t.List[t.Dict[str, t.Any]]]:
    """
    Get the data for a TV show.
    """
    _, resp_tv_series = client.get_tv_series_details(series_id=tv_series_id)
    tv_series = resp_tv_series.json()

    tv_seasons = [
        get_tv_show_season_data_from_tmdb(
            tv_series_id=tv_series_id,
            season_number=season_number,
            client=client,
        )
        for season_number in range(1, tv_series["number_of_seasons"] + 1)
    ]

    return tv_series, tv_seasons


def tmdb_tv_show_data_to_dataclasses(
    tv_series: t.Dict[str, t.Any],
    tv_seasons: t.List[t.Dict[str, t.Any]],
) -> models.TVShow:
    """
    Convert TMDB TV show data to dataclasses.
    """
    transformed_tv_seasons = []

    for tv_season in tv_seasons:
        # Convert the episodes to TVShowEpisode dataclasses.
        episodes = [
            models.TVShowEpisode(
                name=episode["name"],
                episode_number=episode["episode_number"],
                tmdb_id=episode["id"],
            )
            for episode in tv_season["episodes"]
        ]

        # Convert the season to a TVShowSeason dataclass.
        transformed_tv_seasons.append(
            models.TVShowSeason(
                name=tv_season["name"],
                season_number=tv_season["season_number"],
                episodes=episodes,
                tmdb_id=tv_season["id"],
            )
        )

    first_air_date: t.Union[datetime.date, None] = None
    if tv_series["first_air_date"]:
        first_air_date = datetime.datetime.strptime(
            tv_series["first_air_date"], "%Y-%m-%d"
        ).date()

    return models.TVShow(
        name=tv_series["name"],
        description=tv_series["overview"],
        cover_url=f"https://image.tmdb.org/t/p/original{tv_series['poster_path']}",
        seasons=transformed_tv_seasons,
        first_air_date=first_air_date,
        origin_countries=tv_series["origin_country"],
        tmdb_id=tv_series["id"],
    )


def build_tv_show_note(tv_show: models.TVShow) -> str:
    """
    Build the note for a TV show.
    """
    content = render_template("library/tv_show.md", tv_show=tv_show)
    return content.strip()


def build_tv_show_note_name(tv_show: models.TVShow) -> str:
    """
    Build the name for a TV show note.
    """
    return f"{tv_show.name}"


def is_same_tv_show(tv_show: models.TVShow, post: frontmatter.Post) -> bool:
    """
    Check if the TV show data matches the note data.
    """
    return tv_show.tmdb_id == post["tmdb_id"]


def load_tv_show_note(file_path: Path) -> frontmatter.Post:
    """
    Load a TV show note.
    """
    with file_path.open("r") as file_obj:
        post = frontmatter.loads(file_obj.read())
    return post


class AltNoteName(t.TypedDict):

    name: str
    path: Path
    does_exist: bool
    is_same: bool


def list_alternative_note_names(
    tv_show: models.TVShow, config: Config
) -> t.List[AltNoteName]:
    """
    t.List alternative note names for a TV show.
    """
    possible_note_names = [build_tv_show_note_name(tv_show)]

    if tv_show.first_air_date is not None:
        possible_note_names.append(
            f"{tv_show.name} ({tv_show.first_air_date.year})",
        )

    if tv_show.origin_countries:
        possible_note_names.append(
            f"{tv_show.name} ({and_join(tv_show.origin_countries)})",
        )

    note_names = []
    for note_name in possible_note_names:
        note_path = build_tv_show_note_path(note_name, config)
        try:
            post = load_tv_show_note(note_path)
        except FileNotFoundError:
            post = None

        alt_note_name: AltNoteName = {
            "name": note_name,
            "path": note_path,
            "does_exist": note_path.exists(),
            "is_same": (
                is_same_tv_show(tv_show, post) if post is not None else False
            ),
        }
        note_names.append(alt_note_name)

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
) -> t.Generator[t.Tuple[Path, frontmatter.Post], None, None]:
    """
    List the paths of TV show notes.
    """
    # This is just a sanity check. The ensure_required_tv_shows_config function
    # should catch this.
    if not config.TV_SHOWS_DIR_PATH:
        raise ValueError(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    file_paths = sorted(
        config.TV_SHOWS_DIR_PATH.glob("*.md"),
        key=lambda p: p.stem,
    )

    for file_path in file_paths:
        try:
            post = load_tv_show_note(file_path)
        except FileNotFoundError:
            continue

        if has_tmdb_id and "tmdb_id" not in post:
            continue

        yield file_path, post
