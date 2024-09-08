import datetime

import pytest

from obsidian_tools.utils import clock


@pytest.mark.parametrize(
    "start_date, end_date, step, expected_result",
    (
        (
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 5),
            1,
            [
                datetime.date(2024, 1, 1),
                datetime.date(2024, 1, 2),
                datetime.date(2024, 1, 3),
                datetime.date(2024, 1, 4),
                datetime.date(2024, 1, 5),
            ],
        ),
        (
            datetime.date(2024, 1, 1),
            datetime.date(2024, 1, 31),
            7,
            [
                datetime.date(2024, 1, 1),
                datetime.date(2024, 1, 8),
                datetime.date(2024, 1, 15),
                datetime.date(2024, 1, 22),
                datetime.date(2024, 1, 29),
            ],
        ),
    ),
)
def test_get_range_between_dates(start_date, end_date, step, expected_result):
    result = clock.get_range_between_dates(start_date, end_date, step)
    assert result == expected_result


@pytest.mark.parametrize(
    "date, expected_result",
    (
        (datetime.date(2024, 1, 1), datetime.date(2024, 1, 1)),
        (datetime.date(2024, 1, 15), datetime.date(2024, 1, 1)),
        (datetime.date(2024, 1, 31), datetime.date(2024, 1, 1)),
    ),
)
def test_get_start_of_month(date, expected_result):
    result = clock.get_start_of_month(date)
    assert result == expected_result


@pytest.mark.parametrize(
    "date, expected_result",
    (
        (datetime.date(2024, 1, 1), datetime.date(2024, 1, 31)),
        (datetime.date(2024, 1, 15), datetime.date(2024, 1, 31)),
        (datetime.date(2024, 1, 31), datetime.date(2024, 1, 31)),
        (datetime.date(2024, 2, 1), datetime.date(2024, 2, 29)),
    ),
)
def test_get_end_of_month(date, expected_result):
    result = clock.get_end_of_month(date)
    assert result == expected_result
