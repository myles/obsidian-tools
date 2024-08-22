import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:

    VAULT_PATH: Path

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

        safe_keys = (
            "VAULT_PATH",
            "TMDB_API_KEY",
            "LIBRARY_DIR_PATH",
            "BOOKS_DIR_PATH",
            "TV_SHOWS_DIR_PATH",
        )
        to_remove = [key for key in config.keys() if key not in safe_keys]
        for key in to_remove:
            config.pop(key)

        return cls(**config)
