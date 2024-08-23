from pathlib import Path

from obsidian_tools.config import Config


def test_config__from_file(vault_path):
    current_file_path = Path(__file__).parent.resolve()
    example_config_file_path = (
        current_file_path / "example/example-obsidian-tools-config.toml"
    )

    config = Config.from_file(example_config_file_path)

    assert config.VAULT_PATH == vault_path
    assert config.LIBRARY_DIR_PATH == vault_path / "library"
    assert config.BOOKS_DIR_PATH == vault_path / "library" / "books"
    assert config.TV_SHOWS_DIR_PATH == vault_path / "library" / "tv_shows"
