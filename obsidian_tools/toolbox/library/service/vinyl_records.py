from pathlib import Path
from typing import Any, Dict, Union

from sanitize_filename import sanitize

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.integrations import DiscogsClient
from obsidian_tools.toolbox.library.models import Person, VinylRecord, VinylRecordTrack
from obsidian_tools.utils.template import render_template


def ensure_required_vinyl_config(config: Config) -> bool:
    """
    Ensure that the required configuration values for vinyl are set.
    """
    if (
        config.VINYL_RECORDS_DIR_PATH is None
        or config.VINYL_RECORDS_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("VINYL_RECORDS_DIR_PATH")

    if not config.DISCOGS_PERSONAL_ACCESS_TOKEN:
        raise ObsidianToolsConfigError("DISCOGS_PERSONAL_ACCESS_TOKEN")

    return True


def search_vinyl_on_discogs(
    client: DiscogsClient,
    query: Union[str, None],
    barcode: Union[str, None],
) -> Dict[str, Any]:
    """
    Search for a vinyl release on Discogs.
    """
    request, response = client.search(
        query=query,
        barcode=barcode,
        result_type="release",
        result_format="vinyl",
    )
    return response.json()


def get_vinyl_data_from_discogs_release(
    discogs_release_id: int,
    client: DiscogsClient,
) -> Dict[str, Any]:
    """
    Get the vinyl data from Discogs.
    """
    request, response = client.get_release(release_id=discogs_release_id)
    return response.json()


def discogs_release_data_to_dataclass(
    release_data: Dict[str, Any]
) -> VinylRecord:
    """
    Convert Discogs release data to a Vinyl dataclass.
    """
    # Convert the artists to Person dataclasses.
    artists = [
        Person(name=artist["name"]) for artist in release_data["artists"]
    ]

    # Get the ISBN from the identifiers.
    isbn = None
    for identifier in release_data["identifiers"]:
        if identifier["type"] == "Barcode":
            isbn = identifier["value"]
            break

    # Get the primary image URL from the images.
    image_url = None
    try:
        image = next(
            filter(
                lambda i: i["type"] == "primary" and "uri" in i,
                release_data["images"],
            )
        )
        image_url = image["uri"]
    except StopIteration:
        ...

    # Get the track list.
    tracks = [
        VinylRecordTrack(
            title=track["title"],
            position=track["position"],
            duration=track["duration"],
        )
        for track in release_data["tracklist"]
    ]

    return VinylRecord(
        title=release_data["title"],
        artists=artists,
        isbn=isbn,
        image_url=image_url,
        tracks=tracks,
        discogs_id=release_data["id"],
    )


def build_vinyl_note(vinyl_record: VinylRecord) -> str:
    """
    Build the note for a vinyl record.
    """
    content = render_template("library/vinyl.md", vinyl=vinyl_record)
    return content.strip()


def write_vinyl_note(
    note_name: str,
    note_content: str,
    config: Config,
) -> Path:
    """
    Write the note for a book.
    """
    # This is just a sanity check. The ensure_required_books_config function
    # should catch this.
    if not config.VINYL_RECORDS_DIR_PATH:
        raise ValueError(
            "VINYL_RECORDS_DIR_PATH must be set in the configuration file."
        )

    file_name = sanitize(note_name) + ".md"
    file_path = config.VINYL_RECORDS_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
