from typing import List, Union
import datetime
import calendar


def get_range_between_dates(
    start_date: datetime.date,
    end_date: datetime.date
) -> List[datetime.date]:
    """
    Get a list of dates between the start and end date.
    """
    if start_date > end_date:
        raise ValueError("Start date must be before end date.")

    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += datetime.timedelta(days=1)

    return dates


def get_start_of_month(
    date: Union[datetime.date, datetime.datetime]
) -> datetime.date:
    """
    Get the start of the month for the given date.
    """
    return date.replace(day=1)


def get_end_of_month(
    date: Union[datetime.date, datetime.datetime]
) -> datetime.date:
    """
    Get the end of the month for the given date.
    """
    _first_day_of_month, last_day_of_month = calendar.monthrange(date.year, date.month)
    return date.replace(day=last_day_of_month)

