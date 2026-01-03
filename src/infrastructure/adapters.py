"""
This module provides the concrete implementations of the infrastructure interfaces.
"""
import os
import glob
import yaml
import aiofiles
from typing import Any, List, Awaitable

from src.core.interfaces import IConfigSerializer, IFileSystemAdapter
from src.core.models import ProjectConfig

class YamlConfigSerializer(IConfigSerializer):
    """A serializer that uses the PyYAML library."""

    def serialize(self, config: ProjectConfig) -> str:
        """Serializes a ProjectConfig object to a YAML string."""
        # Convert dataclass to dict for serialization
        # A more robust solution might use a custom dumper/representer
        from dataclasses import asdict
        return yaml.dump(asdict(config), sort_keys=False)

    def deserialize(self, data: str) -> Any:
        """Deserializes a YAML string into a dictionary."""
        return yaml.safe_load(data)


class AioFileSystemAdapter(IFileSystemAdapter):
    """An adapter for file system operations using aiofiles."""

    async def file_exists(self, path: str) -> bool:
        """Checks if a file exists asynchronously."""
        # os.path.exists is blocking, but very fast. For a true async version,
        # one might use a thread pool, but this is often acceptable.
        return os.path.exists(path)

    async def read_file(self, path: str) -> str:
        """Reads a file asynchronously."""
        async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
            return await f.read()

    async def write_file(self, path: str, content: str) -> None:
        """Writes to a file asynchronously."""
        async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
            await f.write(content)

    async def find_files(self, pattern: str, root_dir: str) -> List[str]:
        """Finds files matching a glob pattern asynchronously."""
        # glob.glob is blocking. A fully async library like 'aiopath' could be
        # used for larger scale projects, but this is a pragmatic approach.
        return glob.glob(os.path.join(root_dir, pattern), recursive=True)
