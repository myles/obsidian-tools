from datetime import datetime
from typing import Optional

import click


class WeekFormat(click.DateTime):

    name = "week"

    def __init__(self, **kwargs):
        kwargs["formats"] = ["%Y-%W", "%Y-%U"]
        super().__init__(**kwargs)

    def _try_to_convert_date(
        self, value: str, format: str
    ) -> Optional[datetime]:
        value = f"{value}-0"
        format = f"{format}-%w"

        try:
            return datetime.strptime(value, format)
        except ValueError:
            return None

    def __repr__(self) -> str:
        return "Week"


def write_option(func):
    return click.option(
        "-w",
        "--write",
        is_flag=True,
        help="Write the file to the vault.",
    )(func)


def write_force_option(func):
    return click.option(
        "-f",
        "--force",
        is_flag=True,
        help="Force the write operation.",
    )(func)
