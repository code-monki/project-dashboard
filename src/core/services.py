"""
This module implements the services for the Core Logic layer, as defined
in the Detailed Design document.
"""
import os
import json
import threading
import re
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
        self._fs_adapter = fs_adapter
        self._serializer = serializer

    async def load_config(self, project_root: str) -> Optional[ProjectConfig]:
        config_path = os.path.join(project_root, CONFIG_FILE_NAME)
        if not await self._fs_adapter.file_exists(config_path):
            return None

        file_content = await self._fs_adapter.read_file(config_path)
        config_data = self._serializer.deserialize(file_content)
        return ProjectConfig(**config_data)


    async def save_config(self, project_root: str, config: ProjectConfig) -> None:
        config_path = os.path.join(project_root, CONFIG_FILE_NAME)
        serialized_data = self._serializer.serialize(config)
        await self._fs_adapter.write_file(config_path, serialized_data)


class DiscoveryService:
    """Scans for and parses potential targets from build artifacts."""

    def __init__(self, fs_adapter: IFileSystemAdapter):
        self._fs_adapter = fs_adapter

    async def discover_targets(self, project_root: str) -> List[Target]:
        # Discover from all supported sources
        package_json_targets = await self._discover_from_package_json(project_root)
        makefile_targets = await self._discover_from_makefiles(project_root)
        script_targets = await self._discover_from_scripts(project_root)

        # Combine all targets
        all_targets = package_json_targets + makefile_targets + script_targets
        return all_targets

    async def _discover_from_package_json(self, project_root: str) -> List[Target]:
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
                continue
        return targets

    async def _discover_from_makefiles(self, project_root: str) -> List[Target]:
        """
        Discover targets from Makefile and makefile files.

        Parses make targets from Makefiles found in the project.
        """
        targets = []

        # Find both Makefile and makefile
        makefile_files = []
        for pattern in ["**/Makefile", "**/makefile"]:
            files = await self._fs_adapter.find_files(pattern, project_root)
            makefile_files.extend(files)

        # Remove duplicates
        makefile_files = list(set(makefile_files))

        for file_path in makefile_files:
            try:
                content = await self._fs_adapter.read_file(file_path)

                # Parse Makefile targets
                # Target pattern: target_name: [dependencies]
                # Matches lines like: "build:", "test: build", etc.
                target_pattern = re.compile(r'^([a-zA-Z0-9_-]+)\s*:', re.MULTILINE)

                for match in target_pattern.finditer(content):
                    target_name = match.group(1)

                    # Skip special make directives
                    if target_name.startswith('.') and target_name.upper() == target_name:
                        continue  # Skip .PHONY, .DEFAULT, etc.

                    targets.append(
                        Target(
                            name=target_name,
                            command=f"make {target_name}",
                            source_file=file_path,
                        )
                    )
            except Exception:
                # Silently skip malformed Makefiles
                continue

        return targets

    async def _discover_from_scripts(self, project_root: str) -> List[Target]:
        """
        Discover executable scripts (shell and Python).

        Finds .sh and .py files and creates targets that can be executed.
        Excludes common non-script files like setup.py, __init__.py, etc.

        Args:
            project_root: The root directory of the project

        Returns:
            List of Target objects representing executable scripts
        """
        targets = []

        # Files to exclude from script discovery
        excluded_patterns = [
            'setup.py',
            '__init__.py',
            'conftest.py',
        ]

        # Discover shell scripts (.sh files)
        shell_scripts = await self._fs_adapter.find_files("**/*.sh", project_root)
        for script_path in shell_scripts:
            script_name = os.path.basename(script_path)
            targets.append(
                Target(
                    name=script_name,
                    command=f"bash {script_path}",
                    source_file=script_path,
                )
            )

        # Discover Python scripts (.py files)
        python_scripts = await self._fs_adapter.find_files("**/*.py", project_root)
        for script_path in python_scripts:
            script_name = os.path.basename(script_path)

            # Skip excluded files
            if script_name in excluded_patterns:
                continue

            # Skip files in common Python package directories
            if '/src/' in script_path or '/tests/' in script_path or '/__pycache__/' in script_path:
                continue

            targets.append(
                Target(
                    name=script_name,
                    command=f"python {script_path}",
                    source_file=script_path,
                )
            )

        return targets


class ExecutionService:
    """Manages the execution of targets."""

    def __init__(self, shell_adapter: IShellAdapter):
        self._shell_adapter = shell_adapter
        self._running_processes: Dict[int, Any] = {}
        self._lock = threading.Lock()

    async def run_target(self, target: Target, project_root: str, shell: str) -> int:
        process = await self._shell_adapter.execute(target.command, project_root, shell)
        with self._lock:
            self._running_processes[process.pid] = process

        def on_close(pid_to_remove: int):
            with self._lock:
                if pid_to_remove in self._running_processes:
                    del self._running_processes[pid_to_remove]

        process.set_on_close(lambda code: on_close(process.pid))
        return process.pid

    def cancel_target(self, pid: int) -> None:
        with self._lock:
            process = self._running_processes.get(pid)

        if process:
            process.kill()

    def get_running_processes(self) -> List[int]:
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
        self._config_service = config_service
        self._discovery_service = discovery_service
        self._execution_service = execution_service
        self._project_root: Optional[str] = None
        self._config: Optional[ProjectConfig] = None

    async def load_project(self, project_root: str) -> Optional[ProjectConfig]:
        self._project_root = project_root
        config = await self._config_service.load_config(project_root)

        if config:
            self._config = config
        else:
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

    async def run_target(self, target_id: str) -> int:
        if not self._config or not self._project_root:
            raise ValueError("Project not loaded.")

        target_to_run = next((t for t in self._config.targets if t.id == target_id), None)

        if not target_to_run:
            raise ValueError(f"Target with ID '{target_id}' not found.")

        shell = self._config.shell or self._execution_service._shell_adapter.get_system_shell()
        return await self._execution_service.run_target(target_to_run, self._project_root, shell)

    def cancel_target(self, pid: int):
        self._execution_service.cancel_target(pid)

    def get_config(self) -> Optional[ProjectConfig]:
        return self._config