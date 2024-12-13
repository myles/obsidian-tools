import datetime
import typing as t
from pathlib import Path

import frontmatter
from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations import TMDBClient
from obsidian_tools.toolbox.library.models import Movie
from obsidian_tools.utils.humanize import and_join
from obsidian_tools.utils.template import render_template


def ensure_required_movies_config(
    config: Config,
    write: bool,
) -> bool:
    """
    Ensure that the required configuration values for Movies are set.
    """
    if not config.TMDB_API_KEY:
        raise ObsidianToolsConfigError("TMDB_API_KEY")

    if write is True and (
        config.MOVIES_DIR_PATH is None
        or config.MOVIES_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("MOVIES_DIR_PATH")

    return True


def search_movies_on_tmdb(
    client: TMDBClient, query: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Search for a movie on TMDB.
    """
    _, resp_movies = client.search_movies(query=query)
    return resp_movies.json()["results"]


def get_movie_data_from_tmdb(
    movie_id: int,
    client: TMDBClient,
) -> t.Dict[str, t.Any]:
    """
    Get the data for a movie.
    """
    _, resp_movie = client.get_movie_details(movie_id=movie_id)
    movie = resp_movie.json()

    return movie


def tmdb_move_data_to_movie(movie_data: t.Dict[str, t.Any]) -> Movie:
    """
    Transform the data from TMDB to a Movie.
    """
    return Movie(
        title=movie_data["title"],
        tagline=movie_data["tagline"],
        description=movie_data["overview"],
        cover_url=f"https://image.tmdb.org/t/p/original{movie_data['poster_path']}",
        release_date=datetime.datetime.strptime(
            movie_data["release_date"], "%Y-%m-%d"
        ).date(),
        production_countries=[
            country["iso_3166_1"]
            for country in movie_data["production_countries"]
        ],
        tmdb_id=movie_data["id"],
    )


def build_movie_note_name(movie: Movie) -> str:
    """
    Build the name for a Movie note.
    """
    return movie.title


def build_movie_note(movie: Movie) -> str:
    """
    Build the note for a Movie.
    """
    content = render_template("library/movie.md", movie=movie)
    return content.strip()


def build_movie_note_path(note_name: str, config: Config) -> Path:
    """
    Build the path for a Movie note.
    """
    return config.MOVIES_DIR_PATH / (sanitize(note_name) + ".md")


def write_movie_note(
    note_path: Path, note_content: str, config: Config
) -> Path:
    """
    Write the note for a Movie
    """
    # This is just a sanity check. The ensure_required_movies_config function
    # should catch this.
    if not config.MOVIES_DIR_PATH:
        raise ValueError(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    with note_path.open("w") as file_obj:
        file_obj.write(note_content)

    return note_path


def load_movie_note(note_path: Path) -> frontmatter.Post:
    """
    Load a Movie note.
    """
    with note_path.open("r") as file_obj:
        post = frontmatter.load(file_obj)
    return post


def is_same_movie(movie: Movie, post: frontmatter.Post) -> bool:
    """
    Check if the Movie and the Post are the same.
    """
    return movie.tmdb_id == post["tmdb_id"]


class AltNoteName(t.TypedDict):

    name: str
    path: Path
    does_exist: bool
    is_same: bool


def list_alternative_note_names(
    movie: Movie,
    config: Config,
) -> t.List[AltNoteName]:
    """
    List the alternative note names for a Movie.
    """
    possible_names = [build_movie_note_name(movie)]

    if movie.release_date is not None:
        possible_names.append(f"{movie.title} ({movie.release_date.year})")

    if movie.production_countries:
        possible_names.append(
            f"{movie.title} ({and_join(movie.production_countries)})"
        )

    names = []
    for name in possible_names:
        path = build_movie_note_path(name, config)
        try:
            post = load_movie_note(path)
        except FileNotFoundError:
            post = None

        alt_name: AltNoteName = {
            "name": name,
            "path": path,
            "does_exist": path.exists(),
            "is_same": (
                is_same_movie(movie, post) if post is not None else False
            ),
        }
        names.append(alt_name)

    return names
