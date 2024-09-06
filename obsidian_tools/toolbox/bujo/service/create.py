"""
Module for creating Bullet Journal logs.
"""

import datetime
from pathlib import Path

from obsidian_tools.config import Config
from obsidian_tools.toolbox.bujo.models import Day, Month, Week
from obsidian_tools.toolbox.bujo.service import base
from obsidian_tools.utils import clock
from obsidian_tools.utils.template import render_template


def day_to_dataclass(date: datetime.date, config: Config) -> Day:
    """
    Convert a date to a Day dataclass.
    """
    return Day(
        date=date,
        daily_log_file_path=base.get_daily_log_file_path(date, config=config),
    )


def week_to_dataclass(week_date: datetime.date, config: Config) -> Week:
    """
    Convert a start of week date to a Week dataclass.
    """
    start_of_week = clock.get_start_of_week(week_date)
    end_of_week = clock.get_end_of_week(week_date)

    days = [
        day_to_dataclass(day, config)
        for day in clock.get_range_between_dates(start_of_week, end_of_week)
    ]

    calendar_date = start_of_week.isocalendar()

    week_number = f"{calendar_date.year}-{str(calendar_date.week).zfill(2)}"

    return Week(
        week_number=week_number,
        weekly_log_file_path=base.get_weekly_log_file_path(
            start_of_week, config
        ),
        days=days,
    )


def month_to_dataclass(month_date: datetime.date, config: Config) -> Month:
    """
    Convert a month date to a Month dataclass.
    """
    weeks = [
        week_to_dataclass(start_of_week, config)
        for start_of_week in clock.get_range_between_dates(
            clock.get_start_of_month(month_date),
            clock.get_end_of_month(month_date),
            step=7,
        )
    ]

    return Month(
        monthly_log_file_path=base.get_monthly_log_file_path(
            month_date, config
        ),
        weeks=weeks,
    )


def build_monthly_log_note(date: datetime.date, config: Config) -> str:
    """
    Build the content for the monthly log note for the given date.
    """
    month = month_to_dataclass(date, config)

    content = render_template(
        "bujo/monthly_log.md",
        month=month,
    )
    return content.strip()


def build_weekly_log_note(date: datetime.date, config: Config) -> str:
    """
    Build the content for the weekly log note for the given date.
    """
    week = week_to_dataclass(date, config)

    content = render_template("bujo/weekly_log.md", week=week)
    return content.strip()


def write_log_note(file_path: Path, note_content: str) -> Path:
    """
    Write the monthly log note to the vault.
    """
    with file_path.open("w") as file_obj:
        file_obj.write(note_content)

    return file_path
