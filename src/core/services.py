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

import json
from typing import List

from .models import Target

# ... (keep existing ConfigurationService code) ...

class DiscoveryService:
    """Scans for and parses potential targets from build artifacts."""

    def __init__(self, fs_adapter: IFileSystemAdapter):
        """
        Initializes the DiscoveryService.

        Args:
            fs_adapter: An object that implements the IFileSystemAdapter interface.
        """
        self._fs_adapter = fs_adapter

    async def discover_targets(self, project_root: str) -> List[Target]:
        """
        Discovers all potential targets in a project.

        Args:
            project_root: The root directory of the project to scan.

        Returns:
            A list of discovered Target objects.
        """
        package_json_targets = await self._discover_from_package_json(project_root)
        # In the future, we will add calls to discover from Makefiles, etc.
        # and combine the results here.
        return package_json_targets

    async def _discover_from_package_json(self, project_root: str) -> List[Target]:
        """Discovers targets from package.json files."""
        targets = []
        package_json_files = await self._fs_adapter.find_files(
            "**/package.json", project_root
        )

        for file_path in package_json_files:
            try:
                content = await self._fs_adapter.read_file(file_path)
                data = json.loads(content)
                scripts = data.get("scripts", {})
                for name, command in scripts.items():
                    targets.append(
                        Target(
                            name=name,
                            command=f"npm run {name}",
                            source_file=file_path,
                        )
                    )
            except (json.JSONDecodeError, KeyError):
                # Ignore malformed package.json files or files without a scripts section
                continue
        return targets