import json
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class ObsidianConfig:

    core_plugins_enabled: List[str] = field(default_factory=list)

    daily_note_format: Union[str, None] = None
    daily_note_folder: Union[str, None] = None
    daily_note_template: Union[str, None] = None

    @classmethod
    def from_vault(cls, vault_path: Path):
        """
        Load the Obsidian configuration from the vault.
        """
        config = {}

        core_plugins_path = vault_path / ".obsidian" / "core-plugins.json"
        with core_plugins_path.open("rb") as file_obj:
            config["core_plugins_enabled"] = json.load(file_obj)

        daily_notes_path = vault_path / ".obsidian" / "daily-notes.json"
        if daily_notes_path.exists():
            with daily_notes_path.open("rb") as file_obj:
                daily_notes_config = json.load(file_obj)
                for key, value in daily_notes_config.items():
                    config[f"daily_note_{key}"] = value

        return cls(**config)


@dataclass
class Config:

    VAULT_PATH: Path
    OBSIDIAN: ObsidianConfig

    # BuJo configuration
    MONTHLY_NOTE_FORMAT: Optional[str] = None
    MONTHLY_NOTE_FOLDER: Optional[Path] = None

    # Media tools configuration
    TMDB_API_KEY: Optional[str] = None

    LIBRARY_DIR_PATH: Optional[Path] = None
    BOOKS_DIR_PATH: Optional[Path] = None
    TV_SHOWS_DIR_PATH: Optional[Path] = None

    @classmethod
    def from_file(cls, config_file_path: Path):
        config = {}

        if config_file_path is not None:
            with config_file_path.open("rb") as file_obj:
                config = tomllib.load(file_obj)

        if "VAULT_PATH" in config:
            config["VAULT_PATH"] = Path(config["VAULT_PATH"])
        else:
            raise ValueError(
                "VAULT_PATH must be set in the configuration file."
            )

        if "LIBRARY_DIR_PATH" in config:
            config["LIBRARY_DIR_PATH"] = (
                config["VAULT_PATH"] / config["LIBRARY_DIR_PATH"]
            )

        if "BOOKS_DIR_PATH" in config:
            config["BOOKS_DIR_PATH"] = (
                config["LIBRARY_DIR_PATH"] / config["BOOKS_DIR_PATH"]
            )

        if "TV_SHOWS_DIR_PATH" in config:
            config["TV_SHOWS_DIR_PATH"] = (
                config["LIBRARY_DIR_PATH"] / config["TV_SHOWS_DIR_PATH"]
            )

        return cls(**config)
