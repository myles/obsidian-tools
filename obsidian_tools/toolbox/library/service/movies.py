from pathlib import Path
from typing import Any, Dict

from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations import TMDBClient
from obsidian_tools.toolbox.library.models import Movie
from obsidian_tools.utils.template import render_template


def ensure_required_movies_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for Movies are set.
    """
    if (
        config.MOVIES_DIR_PATH is None
        or config.MOVIES_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("MOVIES_DIR_PATH")

    if not config.TMDB_API_KEY:
        raise ObsidianToolsConfigError("TMDB_API_KEY")

    return True


def get_movie_data_from_tmdb(
    movie_id: int,
    client: TMDBClient,
) -> Dict[str, Any]:
    """
    Get the data for a movie.
    """
    _, resp_movie = client.get_movie_details(movie_id=movie_id)
    movie = resp_movie.json()

    return movie


def tmdb_move_data_to_movie(movie_data: Dict[str, Any]) -> Movie:
    """
    Transform the data from TMDB to a Movie.
    """
    return Movie(
        title=movie_data["title"],
        tagline=movie_data["tagline"],
        description=movie_data["overview"],
        cover_url=f"https://image.tmdb.org/t/p/original{movie_data['poster_path']}",
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


def write_movie_note(note_name: str, note_content: str, config: Config) -> Path:
    """
    Write the note for a Movie
    """
    # This is just a sanity check. The ensure_required_movies_config function
    # should catch this.
    if not config.MOVIES_DIR_PATH:
        raise ValueError(
            "TV_SHOWS_DIR_PATH must be set in the configuration file."
        )

    file_name = sanitize(note_name) + ".md"
    file_path = config.MOVIES_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
