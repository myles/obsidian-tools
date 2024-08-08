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

    # Bullet journal configuration
    BUJO_DIR_PATH: Optional[Path] = None

    BUJO_MONTHLY_LOG_DIR_PATH: Optional[Path] = None
    BUJO_MONTHLY_LOG_FILE_PATH_TPL: Optional[str] = None

    BUJO_DAILY_LOG_DIR_PATH: Optional[Path] = None
    BUJO_DAILY_LOG_FILE_PATH_TPL: Optional[str] = None

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

        if "BUJO_DIR_PATH" in config:
            config["BUJO_DIR_PATH"] = (
                config["VAULT_PATH"] / config["BUJO_DIR_PATH"]
            )

        if "BUJO_MONTHLY_LOG_DIR_PATH" in config:
            config["BUJO_MONTHLY_LOG_DIR_PATH"] = (
                config["BUJO_DIR_PATH"] / config["BUJO_MONTHLY_LOG_DIR_PATH"]
            )

        return cls(**config)
