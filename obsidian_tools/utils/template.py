from jinja2 import Environment, PackageLoader, select_autoescape

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
