"""
This module defines the interfaces (protocols) for the Infrastructure Layer.

The Core Logic layer depends on these contracts for all external communication,
allowing for the decoupling of business logic from concrete implementations
like file system access or shell command execution.
"""
from typing import Protocol, List, runtime_checkable, Any, Callable, Awaitable

@runtime_checkable
class IRunningProcess(Protocol):
    """
    Represents a running external process.
    This interface uses callbacks to handle asynchronous events like data,
    errors, and process completion, mirroring the event-driven nature of
    handling subprocesses.
    """
    pid: int

    def set_on_data(self, callback: Callable[[str], None]) -> None:
        """Register a callback for stdout/stderr data."""
        ...

    def set_on_error(self, callback: Callable[[Exception], None]) -> None:
        """Register a callback for process errors (e.g., command not found)."""
        ...

    def set_on_close(self, callback: Callable[[int], None]) -> None:
        """Register a callback for when the process exits, providing the exit code."""
        ...

    def kill(self) -> None:
        """Terminate the process."""
        ...

@runtime_checkable
class IShellAdapter(Protocol):
    """Interface for executing shell commands."""

    def execute(self, command: str, working_dir: str, shell: str) -> IRunningProcess:
        """Executes a command and returns a process handler."""
        ...

    def get_system_shell(self) -> str:
        """Detects the default system shell."""
        ...

@runtime_checkable
class IFileSystemAdapter(Protocol):
    """
    Interface for file system operations.
    Methods are defined as async to handle I/O operations without blocking.
    """

    def file_exists(self, path: str) -> Awaitable[bool]:
        ...

    def read_file(self, path: str) -> Awaitable[str]:
        ...

    def write_file(self, path: str, content: str) -> Awaitable[None]:
        ...

    def find_files(self, pattern: str, root_dir: str) -> Awaitable[List[str]]:
        ...

@runtime_checkable
class IConfigSerializer(Protocol):
    """
    Interface for serializing and deserializing ProjectConfig objects.
    This was an implied dependency for the ConfigurationService.
    """

    def serialize(self, config: Any) -> str:
        """Serializes a ProjectConfig object to a string."""
        ...

    def deserialize(self, data: str) -> Any:
        """Deserializes a string into a ProjectConfig object."""
        ...
