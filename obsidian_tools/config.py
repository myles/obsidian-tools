import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:

    VAULT_PATH: Path

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

        return cls(**config)
