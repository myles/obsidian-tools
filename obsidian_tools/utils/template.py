from jinja2 import Environment, PackageLoader, select_autoescape

from obsidian_tools.utils.momentjs import format as momentjs_format

env = Environment(
    loader=PackageLoader("obsidian_tools"),
    autoescape=select_autoescape(),
)


def render_template(template_name: str, **kwargs) -> str:
    """
    Render a Jinja2 template.
    """
    template = env.get_template(template_name)
    return template.render(**kwargs)


def filter_format_date(value, format_str: str) -> str:
    """
    Filter to format a date using Moment.js.
    """
    return momentjs_format(value, format_str)


env.filters["format_date"] = filter_format_date
