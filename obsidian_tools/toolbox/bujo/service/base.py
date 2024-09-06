import datetime
from pathlib import Path

from obsidian_tools.config import Config
from obsidian_tools.errors import (
    ObsidianToolsConfigError,
    ObsidianToolsPluginNotFoundError,
)
from obsidian_tools.utils.momentjs import format


def ensure_required_config(config: Config) -> bool:
    """
    Ensure that the required configuration values are set.
    """
    if config.MONTHLY_NOTE_FORMAT is None:
        raise ObsidianToolsConfigError("MONTHLY_NOTE_FORMAT")

    if config.MONTHLY_NOTE_FOLDER is None:
        raise ObsidianToolsConfigError("MONTHLY_NOTE_FOLDER")

    if "daily-notes" not in config.OBSIDIAN.core_plugins_enabled:
        raise ObsidianToolsPluginNotFoundError("Daily Notes")

    return True


def get_monthly_log_file_path(
    date: datetime.date,
    config: Config,
) -> Path:
    """
    Get the path to the monthly log folder for the given date.
    """
    if config.MONTHLY_NOTE_FORMAT is None:
        raise ValueError(
            "MONTHLY_NOTE_FORMAT must be set in the configuration."
        )

    file_stem = format(date, config.MONTHLY_NOTE_FORMAT)
    file_name = f"{file_stem}.md"

    # If the monthly note folder is not set, return the file path in the vault.
    if config.MONTHLY_NOTE_FOLDER is None:
        return config.VAULT_PATH / file_name
    return config.MONTHLY_NOTE_FOLDER / file_name


def get_weekly_log_file_path(date: datetime.date, config: Config) -> Path:
    """
    Get the path to the weekly log folder for the given date.
    """
    if config.WEEKLY_NOTE_FORMAT is None:
        raise ValueError("WEEKLY_NOTE_FORMAT must be set in the configuration.")

    file_stem = format(date, config.WEEKLY_NOTE_FORMAT)
    file_name = f"{file_stem}.md"

    # If the weekly note folder is not set, return the file path in the vault.
    if config.WEEKLY_NOTE_FOLDER is None:
        return config.VAULT_PATH / file_name
    return config.WEEKLY_NOTE_FOLDER / file_name


def get_daily_log_file_path(
    date: datetime.date,
    config: Config,
) -> Path:
    """
    Get the file name for the daily log for the given date.
    """
    if config.OBSIDIAN.daily_note_format is None:
        raise ValueError("daily_note_format must be set in the configuration.")

    file_stem = format(date, config.OBSIDIAN.daily_note_format)
    file_name = f"{file_stem}.md"

    # If the daily note folder is not set, return the file path in the vault.
    if config.OBSIDIAN.daily_note_folder is None:
        return config.VAULT_PATH / file_name
    return config.VAULT_PATH / config.OBSIDIAN.daily_note_folder / file_name
