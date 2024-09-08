from dataclasses import replace

import pytest

from obsidian_tools.errors import ObsidianToolsConfigError
from obsidian_tools.toolbox.library.service import core


def test_ensure_required_config(mock_config):
    good_config = replace(
        mock_config,
        LIBRARY_DIR_PATH=mock_config.VAULT_PATH / "library",
    )
    assert core.ensure_required_config(good_config) is True

    bad_config = replace(mock_config, LIBRARY_DIR_PATH=None)

    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        core.ensure_required_config(bad_config)

    assert str(exc_info.value.config_key) == "LIBRARY_DIR_PATH"
