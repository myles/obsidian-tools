import pytest

from obsidian_tools.config import Config
from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.toolbox.library.service import core


def test_ensure_required_config(vault_path):
    good_config = Config(
        VAULT_PATH=vault_path,
        LIBRARY_DIR_PATH=vault_path / "library",
    )
    assert core.ensure_required_config(good_config) is True

    bad_config = Config(VAULT_PATH=vault_path)
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        core.ensure_required_config(bad_config)

    assert str(exc_info.value.config_key) == "LIBRARY_DIR_PATH"
