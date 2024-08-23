from dataclasses import dataclass, field
from typing import List, Optional
import datetime
from obsidian_tools.utils.humanize import and_join

@dataclass
class Person:
    name: str


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


@dataclass
class Track:

    title: str
    position: str
    duration: str


@dataclass
class Vinyl:

    title: str
    artists: List[Person] = field(default_factory=list)
    isbn: Optional[str] = None
    image_url: Optional[str] = None

    tracklist: List[Track] = field(default_factory=list)

    # Source-specific identifiers.
    discogs_id: Optional[str] = None

    @property
    def display_artists(self) -> str:
        return and_join([artist.name for artist in self.artists])


