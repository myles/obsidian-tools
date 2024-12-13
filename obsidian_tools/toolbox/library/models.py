import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from obsidian_tools.utils.humanize import and_join


@dataclass
class Person:
    name: str

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


@dataclass
class Book:

    title: str
    authors: List[Person] = field(default_factory=list)
    number_of_pages: Optional[int] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None

    # Source-specific identifiers.
    google_book_id: Optional[str] = None
    openlibrary_book_id: Optional[str] = None

    @property
    def display_authors(self) -> str:
        return and_join([author.name for author in self.authors])

    def __eq__(self, other):
        if self.isbn and other.isbn:
            return self.isbn == other.isbn
        elif self.google_book_id and other.google_book_id:
            return self.google_book_id == other.google_book_id
        elif self.openlibrary_book_id and other.openlibrary_book_id:
            return self.openlibrary_book_id == other.openlibrary_book_id

        return False

    def __hash__(self):
        if self.isbn:
            return hash(self.isbn)
        elif self.google_book_id:
            return hash(self.google_book_id)
        elif self.openlibrary_book_id:
            return hash(self.openlibrary_book_id)

        return hash(self.title)


@dataclass
class Movie:

    title: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None

    release_date: Optional[datetime.date] = None
    production_countries: List[str] = field(default_factory=list)

    # Source-specific identifiers.
    tmdb_id: Optional[str] = None


@dataclass
class TVShowEpisode:

    name: str
    episode_number: int

    # Source-specific identifiers.
    tmdb_id: Optional[str] = None


@dataclass
class TVShowSeason:

    name: str
    season_number: int
    episodes: List[TVShowEpisode] = field(default_factory=list)

    # Source-specific identifiers.
    tmdb_id: Optional[str] = None

    def __post_init__(self):
        # Sort the episodes by episode number.
        self.episodes = sorted(self.episodes, key=lambda e: e.episode_number)


@dataclass
class TVShow:

    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None

    first_air_date: Optional[datetime.date] = None
    origin_countries: List[str] = field(default_factory=list)

    seasons: List[TVShowSeason] = field(default_factory=list)

    # Source-specific identifiers.
    tmdb_id: Optional[str] = None

    def __post_init__(self):
        # Sort the seasons by season number.
        self.seasons = sorted(self.seasons, key=lambda s: s.season_number)


@dataclass
class VideoGame:

    title: str
    description: Optional[str] = None
    cover_url: Optional[str] = None

    first_release_date: Optional[datetime.date] = None

    # Source-specific identifiers.
    igdb_id: Optional[str] = None
    steam_id: Optional[str] = None


@dataclass
class VinylRecordTrack:

    title: str
    position: str
    duration: str


@dataclass
class VinylRecord:

    title: str
    artists: List[Person] = field(default_factory=list)
    isbn: Optional[str] = None
    image_url: Optional[str] = None

    tracks: List[VinylRecordTrack] = field(default_factory=list)

    # Source-specific identifiers.
    discogs_id: Optional[str] = None

    @property
    def display_artists(self) -> str:
        return and_join([artist.name for artist in self.artists])
