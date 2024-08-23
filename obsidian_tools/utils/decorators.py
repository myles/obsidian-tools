import click


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
