from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError


def ensure_required_config(config: Config) -> bool:
    """
    Ensure that the required configuration values are set.
    """
    if (
        config.LIBRARY_DIR_PATH is None
        or config.LIBRARY_DIR_PATH.exists() is False
    ):
        raise ObsidianToolsConfigError("LIBRARY_DIR_PATH")

    return True
