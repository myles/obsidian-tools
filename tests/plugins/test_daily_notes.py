import datetime
from pathlib import Path
from typing import Union

import pytest

from obsidian_tools.config import Config, ObsidianConfig
from obsidian_tools.plugins import daily_notes


@pytest.mark.parametrize(
    "vault_path, daily_note_format, daily_note_folder, date, expected_result",
    (
        (
            Path("/tmp/vault"),
            None,
            None,
            datetime.date(2022, 1, 1),
            Path("/tmp/vault/2022-01-01"),
        ),
    ),
)
def test_get_path_for_daily_note(
    vault_path: Path,
    daily_note_format: Union[str, None],
    daily_note_folder: Union[str, None],
    date: datetime.date,
    expected_result: Path,
):
    config = Config(
        VAULT_PATH=vault_path,
        OBSIDIAN=ObsidianConfig(
            core_plugins_enabled=["daily-notes"],
            daily_note_format=daily_note_format,
            daily_note_folder=daily_note_folder,
        ),
    )

    result = daily_notes.get_path_for_daily_note(date, config)
    assert result == expected_result
