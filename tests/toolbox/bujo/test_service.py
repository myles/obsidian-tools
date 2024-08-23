import datetime

import pytest

from obsidian_tools.errors import ObsidianToolsConfigError, ObsidianToolsPluginNotFoundError
from obsidian_tools.toolbox.bujo import service


def test_ensure_required_config(mock_config):
    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        service.ensure_required_config(mock_config)
    assert str(exc_info.value.config_key) == "MONTHLY_NOTE_FORMAT"

    # Set the first required config value
    mock_config.MONTHLY_NOTE_FORMAT = "YYYY-MM"

    with pytest.raises(ObsidianToolsConfigError) as exc_info:
        service.ensure_required_config(mock_config)
    assert str(exc_info.value.config_key) == "MONTHLY_NOTE_FOLDER"

    # Set the second required config value
    mock_config.MONTHLY_NOTE_FOLDER = mock_config.VAULT_PATH / "bujo"

    with pytest.raises(ObsidianToolsPluginNotFoundError) as exc_info:
        service.ensure_required_config(mock_config)
    assert str(exc_info.value.plugin_name) == "Daily Notes"

    # Set the third required config value
    mock_config.OBSIDIAN.core_plugins_enabled = ["daily-notes"]

    assert service.ensure_required_config(mock_config) is True


def test_get_range_between_dates():
    start_date = datetime.date(2024, 8, 1)
    end_date = datetime.date(2024, 8, 31)

    dates = service.get_range_between_dates(start_date, end_date)
    assert len(dates) == 31


def test_get_start_of_month():
    start_of_month = service.get_start_of_month(datetime.date(2024, 8, 15))
    assert start_of_month == datetime.date(2024, 8, 1)


def test_get_end_of_month():
    end_of_month = service.get_end_of_month(datetime.date(2024, 8, 15))
    assert end_of_month == datetime.date(2024, 8, 31)


def test_get_monthly_log_file_path(mock_config_for_bujo):
    date = datetime.date(2024, 8, 1)
    file_path = service.get_monthly_log_file_path(date, mock_config_for_bujo)
    assert file_path == mock_config_for_bujo.VAULT_PATH / "monthly-logs/2024-08.md"
