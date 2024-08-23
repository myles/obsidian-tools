import datetime
from pathlib import Path
from typing import List, Union, TypedDict

from obsidian_tools.config import Config
from obsidian_tools.errors import (
    ObsidianToolsConfigError,
    ObsidianToolsPluginNotFoundError,
)
from obsidian_tools.utils.clock import get_range_between_dates, get_end_of_month, get_start_of_month
from obsidian_tools.utils.momentjs import format
from obsidian_tools.utils.template import render_template


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
    date: Union[datetime.date, datetime.datetime],
    config: Config,
) -> Path:
    """
    Get the path to the monthly log folder for the given date.
    """
    file_name = format(date, config.MONTHLY_NOTE_FORMAT)
    return config.MONTHLY_NOTE_FOLDER / f"{file_name}.md"


def get_daily_log_file_path(
    date: Union[datetime.date, datetime.datetime],
    config: Config,
) -> Path:
    """
    Get the file name for the daily log for the given date.
    """
    file_name = format(date, config.OBSIDIAN.daily_note_format)
    return (
        config.VAULT_PATH
        / config.OBSIDIAN.daily_note_folder
        / f"{file_name}.md"
    )


class MonthlyLogDayContext(TypedDict):
    date: datetime.date
    week_number: str
    daily_log_file_name: str


class MonthlyLogContext(TypedDict):
    start_of_month: datetime.date
    end_of_month: datetime.date
    start_of_next_month: datetime.date
    start_of_previous_month: datetime.date
    days: List[MonthlyLogDayContext]


def get_monthly_log_context_for_day(
    date: Union[datetime.date, datetime.datetime],
    config: Config,
) -> MonthlyLogDayContext:
    """
    Get the context for the monthly log template for the given date.
    """
    return {
        "date": date if isinstance(date, datetime.date) else date.date(),
        "week_number": f"{date.isocalendar().year}-{date.isocalendar().week}",
        "daily_log_file_name": get_daily_log_file_path(date, config).stem,
    }


def get_monthly_log_context(
    month_date: Union[datetime.date, datetime.datetime],
    config: Config,
) -> MonthlyLogContext:
    """
    Get the context for the monthly log template.
    """
    start_of_month = get_start_of_month(month_date)
    end_of_month = get_end_of_month(month_date)

    start_of_next_month = get_start_of_month(end_of_month + datetime.timedelta(days=1))
    start_of_previous_month = get_start_of_month(start_of_month - datetime.timedelta(days=1))

    days = []
    for day_date in get_range_between_dates(start_of_month, end_of_month):
        days.append(get_monthly_log_context_for_day(day_date, config))

    return {
        "start_of_month": start_of_month,
        "end_of_month": end_of_month,
        "start_of_next_month": start_of_next_month,
        "start_of_previous_month": start_of_previous_month,
        "days": days,
    }


def build_monthly_log_note(
    date: Union[datetime.date, datetime.datetime],
    config: Config,
) -> str:
    """
    Build the content for the monthly log note for the given date.
    """
    context = get_monthly_log_context(date, config)
    content = render_template("bujo/monthly_log.md", **context)
    return content.strip()


def get_monthly_log_path(
    date: Union[datetime.date, datetime.datetime],
    config: Config,
) -> Path:
    """
    Get the path to the monthly log note for the given date.
    """
    if not config.MONTHLY_NOTE_FOLDER:
        raise ValueError(
            "MONTHLY_NOTE_FOLDER must be set in the configuration file."
        )

    note_name = format(date, config.MONTHLY_NOTE_FORMAT)

    file_name = f"{note_name}.md"
    return config.MONTHLY_NOTE_FOLDER / file_name


def write_monthly_log_note(file_path: Path, note_content: str) -> Path:
    """
    Write the monthly log note to the vault.
    """
    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
