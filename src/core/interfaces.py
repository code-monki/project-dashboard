"""
This module defines the interfaces for the Infrastructure Layer.
These interfaces define the contract that the Infrastructure Layer must fulfill.
The Core Logic layer codes against these interfaces, not the concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import List


class IConfigSerializer(ABC):
    """Interface for configuration serialization and deserialization."""

    @abstractmethod
    def serialize(self, config: 'ProjectConfig') -> str:
        """
        Serialize a ProjectConfig object to a string format (e.g., YAML, JSON).

        Args:
            config: The ProjectConfig object to serialize

        Returns:
            A string representation of the configuration
        """
        pass

    @abstractmethod
    def deserialize(self, data: str) -> dict:
        """
        Deserialize a string to a dictionary representation of configuration.

        Args:
            data: The serialized configuration string

        Returns:
            A dictionary containing the configuration data
        """
        pass


class IFileSystemAdapter(ABC):
    """Interface for file system operations."""

    @abstractmethod
    async def file_exists(self, path: str) -> bool:
        """
        Check if a file exists at the given path.

        Args:
            path: The file path to check

        Returns:
            True if the file exists, False otherwise
        """
        pass

    @abstractmethod
    async def read_file(self, path: str) -> str:
        """
        Read the contents of a file.

        Args:
            path: The file path to read

        Returns:
            The file contents as a string
        """
        pass

    @abstractmethod
    async def write_file(self, path: str, content: str) -> None:
        """
        Write content to a file.

        Args:
            path: The file path to write to
            content: The content to write
        """
        pass

    @abstractmethod
    async def find_files(self, pattern: str, root_dir: str) -> List[str]:
        """
        Find files matching a pattern within a root directory.

        Args:
            pattern: The glob pattern to match (e.g., "**/*.json")
            root_dir: The root directory to search from

        Returns:
            A list of file paths that match the pattern
        """
        pass


class IRunningProcess(ABC):
    """
    Represents a running process.
    Provides methods to interact with and monitor the process.

    Note: Implementations must provide a 'pid' attribute (not necessarily a property).
    """

    # Note: pid is expected to be set as an instance attribute in __init__
    # No @abstractmethod needed as it will be set dynamically
    pid: int

    @abstractmethod
    def set_on_data(self, callback) -> None:
        """
        Set a callback to be invoked when data (stdout/stderr) is received.

        Args:
            callback: A callable that takes a string argument (the data chunk)
        """
        pass

    @abstractmethod
    def set_on_error(self, callback) -> None:
        """
        Set a callback to be invoked when an error occurs.

        Args:
            callback: A callable that takes an Exception argument
        """
        pass

    @abstractmethod
    def set_on_close(self, callback) -> None:
        """
        Set a callback to be invoked when the process closes.

        Args:
            callback: A callable that takes an integer argument (the exit code)
        """
        pass

    @abstractmethod
    def kill(self) -> None:
        """Terminate the running process."""
        pass


class IShellAdapter(ABC):
    """Interface for shell command execution."""

    @abstractmethod
    async def execute(self, command: str, working_dir: str, shell: str) -> IRunningProcess:
        """
        Execute a shell command and return a handle to the running process.

        Args:
            command: The command to execute
            working_dir: The working directory for the command
            shell: The shell executable to use (e.g., "/bin/bash", "/bin/sh")

        Returns:
            An IRunningProcess instance representing the running command
        """
        pass

    @abstractmethod
    def get_system_shell(self) -> str:
        """
        Detect and return the default system shell path.

        Returns:
            The path to the system's default shell
        """
        pass
