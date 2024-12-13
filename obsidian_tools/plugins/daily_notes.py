import datetime
from pathlib import Path

from obsidian_tools.config import Config
from obsidian_tools.utils.momentjs import format as momentjs_format


def get_path_for_daily_note(date: datetime.date, config: Config) -> Path:
    """
    Get the path for a daily note.
    """
    vault_path = config.VAULT_PATH

    # Get the daily note format and folder from the configuration.
    daily_note_format = config.OBSIDIAN.daily_note_format or "YYYY-MM-DD"
    daily_note_folder = config.OBSIDIAN.daily_note_folder or ""

    # Format the file name.
    file_stem = momentjs_format(date, daily_note_format)
    file_name = f"{file_stem}.md"

    return vault_path / daily_note_folder / file_name
