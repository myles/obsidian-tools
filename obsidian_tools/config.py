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

    @classmethod
    def from_vault(cls, vault_path: Path):
        """
        Load the Obsidian configuration from the vault.
        """
        config = {}

        core_plugins_path = vault_path / ".obsidian" / "core-plugins.json"
        if core_plugins_path.exists():
            with core_plugins_path.open("rb") as file_obj:
                config["core_plugins_enabled"] = json.load(file_obj)

        daily_notes_path = vault_path / ".obsidian" / "daily-notes.json"
        if daily_notes_path.exists():
            with daily_notes_path.open("rb") as file_obj:
                daily_notes_config = json.load(file_obj)

            config["daily_note_format"] = (
                daily_notes_config.get("format") or None
            )
            config["daily_note_folder"] = (
                daily_notes_config.get("folder") or None
            )

        return cls(**config)


@dataclass
class Config:

    VAULT_PATH: Path
    OBSIDIAN: ObsidianConfig

    # OpenAI configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ORGANIZATION_ID: Optional[str] = None
    OPENAI_PROJECT_ID: Optional[str] = None

    # BuJo configuration
    MONTHLY_NOTE_FORMAT: Optional[str] = None
    MONTHLY_NOTE_FOLDER: Optional[Path] = None

    WEEKLY_NOTE_FORMAT: Optional[str] = None
    WEEKLY_NOTE_FOLDER: Optional[Path] = None

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
            vault_path = Path(config["VAULT_PATH"])
        else:
            raise ValueError(
                "VAULT_PATH must be set in the configuration file."
            )

        if vault_path.is_absolute() is True:
            config["VAULT_PATH"] = vault_path
        else:
            config["VAULT_PATH"] = config_file_path.parent / vault_path

        config["OBSIDIAN"] = ObsidianConfig.from_vault(config["VAULT_PATH"])

        transform_to_path_root_keys = (
            "MONTHLY_NOTE_FOLDER",
            "WEEKLY_NOTE_FOLDER",
            "LIBRARY_DIR_PATH",
        )
        for key in transform_to_path_root_keys:
            if key in config:
                config[key] = config["VAULT_PATH"] / config[key]

        transform_to_path_library_keys = (
            "BOOKS_DIR_PATH",
            "TV_SHOWS_DIR_PATH",
        )
        for key in transform_to_path_library_keys:
            if key in config:
                config[key] = config["LIBRARY_DIR_PATH"] / config[key]

        safe_keys = (
            "VAULT_PATH",
            "OBSIDIAN",
            "OPENAI_API_KEY",
            "OPENAI_ORGANIZATION_ID",
            "OPENAI_PROJECT_ID",
            "MONTHLY_NOTE_FOLDER",
            "MONTHLY_NOTE_FORMAT",
            "WEEKLY_NOTE_FOLDER",
            "WEEKLY_NOTE_FORMAT",
            "TMDB_API_KEY",
            "LIBRARY_DIR_PATH",
            "BOOKS_DIR_PATH",
            "TV_SHOWS_DIR_PATH",
        )
        to_remove = [key for key in config.keys() if key not in safe_keys]
        for key in to_remove:
            config.pop(key)

        return cls(**config)
