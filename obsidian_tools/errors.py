class ObsidianToolsError(Exception):
    """
    Base class for all ObsidianTools errors.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ObsidianToolsConfigError(ObsidianToolsError):
    """
    Raised when there is an error with the configuration.
    """

    def __init__(self, config_key: str):
        self.config_key = config_key
        super().__init__(
            f"{self.config_key} must be set in the configuration file."
        )


class ObsidianToolsPluginNotFoundError(ObsidianToolsError):
    """
    Raised when a plugin is not found in the Obsidian vault.
    """

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        super().__init__(f"{self.plugin_name} plugin not found in the vault.")
