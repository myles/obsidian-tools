from jinja2 import Environment, PackageLoader, select_autoescape
import datetime
from typing import Union
import arrow

environment = Environment(
    loader=PackageLoader("obsidian_tools"),
    autoescape=select_autoescape(),
)


def render_template(template_name: str, **kwargs) -> str:
    """
    Render a Jinja2 template.
    """
    template = environment.get_template(template_name)
    return template.render(**kwargs)


def filter_date(value: Union[datetime.date, datetime.datetime], date_format="Do MMMM, YYYY") -> str:
    """
    Format the date using the given format.
    """
    date = arrow.get(value)
    return date.format(date_format)


environment.filters["date"] = filter_date
