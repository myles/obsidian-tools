from pathlib import Path
from typing import List, Union

import click

from obsidian_tools.config import Config


class ObsidianToolsCLI(click.MultiCommand):

    tools_dir_path = Path(__file__).parent / "tools"

    def list_commands(self, ctx: click.Context) -> List[str]:
        rv = []

        for filename in self.tools_dir_path.glob("*/cli.py"):
            rv.append(filename.parent.name)

        rv.sort()
        return rv

    def get_command(
        self, ctx: click.Context, name: str
    ) -> Union[click.Command, None]:
        ns = {}  # type: ignore

        tool_cli_path = self.tools_dir_path / name / "cli.py"

        if tool_cli_path.exists() is False:
            return None

        with tool_cli_path.open() as file_obj:
            code = compile(file_obj.read(), tool_cli_path, "exec")
            eval(code, ns, ns)

        return ns["cli"]


@click.group(  # type: ignore
    cls=ObsidianToolsCLI,
    context_settings={"allow_interspersed_args": False},
)
@click.option(
    "-c",
    "--config",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
    ),
    help="Path to the configuration file.",
)
@click.pass_context
def cli(ctx: click.Context, config: Union[str, None]):
    """
    CLI tools for interacting with Obsidian vaults.
    """
    ctx.ensure_object(dict)

    if config:
        config_file_path = Path(config)
    else:
        config_file_path = Path.home() / ".obsidian-tools-config.toml"

    if config_file_path.exists() is False:
        config_file_path = Path.cwd() / "obsidian-tools-config.toml"

    ctx.obj["config"] = Config.from_file(config_file_path=config_file_path)
