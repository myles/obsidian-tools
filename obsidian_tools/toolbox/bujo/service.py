from typing import Generator, Dict, Union, List, Any
import datetime
from sanitize_filename import sanitize
from pathlib import Path
from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.utils.template import render_template
import arrow


def ensure_required_config(config: Config) -> bool:
    """
    Ensure that the required configuration values are set.
    """
    if (
        config.BUJO_DIR_PATH is None
        or config.BUJO_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("BUJO_DIR_PATH")

    return True


def get_days_in_range(start_date: datetime.date, end_date: datetime.date) -> Generator[datetime.date, None, None]:
    """
    Get the range of dates between the start and end date.
    """
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)


def get_monthly_log_context(date: datetime.date) -> Dict[str, Any]:
    """
    Build the monthly log context for the given date.
    """
    # Get the first and last day of the month.
    first_day_of_month = date.replace(day=1)
    last_day_of_month = date.replace(day=1, month=date.month + 1) - datetime.timedelta(days=1)

    # Get the range of dates for the month.
    days_in_month = []

    for day in get_days_in_range(first_day_of_month, last_day_of_month):
        weekly_log = f'CW{day.strftime("%-W")} {day.strftime("%Y")}'
        days_in_month.append({"day": day, "weekly_log": weekly_log})

    return {
        "first_day_of_month": first_day_of_month,
        "last_day_of_month": last_day_of_month,
        "days_in_month": days_in_month,
    }


def build_monthly_log_note(context: Dict[str, Any]) -> str:
    """
    Build the monthly log note.
    """
    content = render_template("bujo/monthly_log.md", **context)
    return content.strip()


def build_monthly_log_file_name(date: datetime.date, config: Config) -> str:
    """
    Build the file name for the monthly log note.
    """
    return arrow.get(date).format(config.BUJO_MONTHLY_LOG_FILE_PATH_TPL)


def write_monthly_log_note(
    note_name: str,
    note_content: str,
    config: Config,
) -> Path:
    """
    Write the note for a book.
    """
    file_name = sanitize(note_name) + ".md"
    file_path = config.BUJO_MONTHLY_LOG_DIR_PATH / file_name

    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
