"""
This module implements the services for the Core Logic layer, as defined
in the Detailed Design document.
"""
import os
from typing import Optional

from .interfaces import IFileSystemAdapter, IConfigSerializer
from .models import ProjectConfig

CONFIG_FILE_NAME = ".project-dashboard.yml"

class ConfigurationService:
    """Manages the loading and saving of the ProjectConfig."""

    def __init__(
        self,
        fs_adapter: IFileSystemAdapter,
        serializer: IConfigSerializer,
    ):
        """
        Initializes the ConfigurationService.

        Args:
            fs_adapter: An object that implements the IFileSystemAdapter interface.
            serializer: An object that implements the IConfigSerializer interface.
        """
        self._fs_adapter = fs_adapter
        self._serializer = serializer

    async def load_config(self, project_root: str) -> Optional[ProjectConfig]:
        """
        Loads the project configuration from the specified root directory.

        Args:
            project_root: The root directory of the project.

        Returns:
            A ProjectConfig object if the configuration file is found and valid,
            otherwise None.
        """
        config_path = os.path.join(project_root, CONFIG_FILE_NAME)
        if not await self._fs_adapter.file_exists(config_path):
            return None

        file_content = await self._fs_adapter.read_file(config_path)
        config_data = self._serializer.deserialize(file_content)
        # A more robust implementation would validate the deserialized data
        # before creating the ProjectConfig object.
        return ProjectConfig(**config_data)


    async def save_config(self, project_root: str, config: ProjectConfig) -> None:
        """
        Saves the project configuration to the specified root directory.

        Args:
            project_root: The root directory of the project.
            config: The ProjectConfig object to save.
        """
        config_path = os.path.join(project_root, CONFIG_FILE_NAME)
        serialized_data = self._serializer.serialize(config)
        await self._fs_adapter.write_file(config_path, serialized_data)
