"""
This module implements the services for the Core Logic layer, as defined
in the Detailed Design document.
"""
import os
import json
import threading
from typing import Optional, List, Dict, Any

from .interfaces import IFileSystemAdapter, IConfigSerializer, IShellAdapter
from .models import ProjectConfig, Target

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


class ExecutionService:
    """Manages the execution of targets."""

    def __init__(self, shell_adapter: IShellAdapter):
        """
        Initializes the ExecutionService.

        Args:
            shell_adapter: An object that implements the IShellAdapter interface.
        """
        self._shell_adapter = shell_adapter
        self._running_processes: Dict[int, Any] = {}
        self._lock = threading.Lock()

    def run_target(self, target: Target, project_root: str, shell: str) -> int:
        """
        Runs a target command and tracks the process.

        Args:
            target: The Target object to run.
            project_root: The root directory of the project.
            shell: The shell to use for execution.

        Returns:
            The process ID (pid) of the spawned process.
        """
        process = self._shell_adapter.execute(target.command, project_root, shell)
        with self._lock:
            self._running_processes[process.pid] = process

        # Set up a callback to remove the process from tracking when it closes
        def on_close(pid_to_remove: int):
            with self._lock:
                if pid_to_remove in self._running_processes:
                    del self._running_processes[pid_to_remove]

        process.set_on_close(lambda code: on_close(process.pid))

        return process.pid

    def cancel_target(self, pid: int) -> None:
        """
        Cancels a running target by its process ID.

        Args:
            pid: The process ID of the target to cancel.
        """
        with self._lock:
            process = self._running_processes.get(pid)

        if process:
            process.kill()
            # The on_close callback will handle removal from the dictionary

    def get_running_processes(self) -> List[int]:
        """
        Gets a list of currently running process IDs.

        Returns:
            A list of integers representing the PIDs.
        """
        with self._lock:
            return list(self._running_processes.keys())

class ProjectService:
    """
    Acts as the primary entry point for the UI layer, orchestrating the other
    services to provide a unified API for all project-related operations.
    """

    def __init__(
        self,
        config_service: ConfigurationService,
        discovery_service: DiscoveryService,
        execution_service: ExecutionService,
    ):
        """
        Initializes the ProjectService facade.

        Args:
            config_service: An instance of ConfigurationService.
            discovery_service: An instance of DiscoveryService.
            execution_service: An instance of ExecutionService.
        """
        self._config_service = config_service
        self._discovery_service = discovery_service
        self._execution_service = execution_service
        self._project_root: Optional[str] = None
        self._config: Optional[ProjectConfig] = None

    async def load_project(self, project_root: str) -> Optional[ProjectConfig]:
        """
        Loads a project, either from a config file or by discovering targets.
        If no config file exists, a new one is created and saved.

        Args:
            project_root: The absolute path to the project's root directory.

        Returns:
            The loaded or newly created ProjectConfig.
        """
        self._project_root = project_root
        config = await self._config_service.load_config(project_root)

        if config:
            self._config = config
        else:
            # No config file found, so discover targets and create a new config
            discovered_targets = await self._discovery_service.discover_targets(
                project_root
            )
            project_name = os.path.basename(project_root)
            new_config = ProjectConfig(
                project_name=project_name, targets=discovered_targets
            )
            await self._config_service.save_config(project_root, new_config)
            self._config = new_config

        return self._config

    def run_target(self, target_id: str) -> int:
        """
        Runs a target by its ID.

        Args:
            target_id: The ID of the target to run.

        Returns:
            The PID of the started process.

        Raises:
            ValueError: If the project is not loaded or the target ID is not found.
        """
        if not self._config or not self._project_root:
            raise ValueError("Project not loaded.")

        target_to_run = next((t for t in self._config.targets if t.id == target_id), None)

        if not target_to_run:
            raise ValueError(f"Target with ID '{target_id}' not found.")

        shell = self._config.shell or self._execution_service._shell_adapter.get_system_shell()
        return self._execution_service.run_target(target_to_run, self._project_root, shell)

    def cancel_target(self, pid: int):
        """Cancels a running target by its PID."""
        self._execution_service.cancel_target(pid)

    def get_config(self) -> Optional[ProjectConfig]:
        """Returns the currently loaded project configuration."""
        return self._config
