"""
This module provides the concrete implementations of the infrastructure interfaces.
"""
import os
import glob
import yaml
import aiofiles
import asyncio
import shutil
from typing import Any, List, Callable

from src.core.interfaces import IConfigSerializer, IFileSystemAdapter, IRunningProcess, IShellAdapter
from src.core.models import ProjectConfig


class YamlConfigSerializer(IConfigSerializer):
    """A serializer that uses the PyYAML library."""

    def serialize(self, config: ProjectConfig) -> str:
        from dataclasses import asdict
        return yaml.dump(asdict(config), sort_keys=False)

    def deserialize(self, data: str) -> Any:
        return yaml.safe_load(data)


class AioFileSystemAdapter(IFileSystemAdapter):
    """An adapter for file system operations using aiofiles."""

    async def file_exists(self, path: str) -> bool:
        return await asyncio.to_thread(os.path.exists, path)

    async def read_file(self, path: str) -> str:
        async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
            return await f.read()

    async def write_file(self, path: str, content: str) -> None:
        async with aiofiles.open(path, mode='w', encoding='utf-8') as f:
            await f.write(content)

    async def find_files(self, pattern: str, root_dir: str) -> List[str]:
        return await asyncio.to_thread(glob.glob, os.path.join(root_dir, pattern), recursive=True)


class AsyncioRunningProcess(IRunningProcess):
    """An implementation of IRunningProcess using asyncio.subprocess."""

    def __init__(self, process: asyncio.subprocess.Process):
        self._process = process
        self.pid = process.pid
        self._on_data: Callable[[str], None] = lambda data: None
        self._on_error: Callable[[Exception], None] = lambda err: None
        self._on_close: Callable[[int], None] = lambda code: None

    def set_on_data(self, callback: Callable[[str], None]) -> None:
        self._on_data = callback

    def set_on_error(self, callback: Callable[[Exception], None]) -> None:
        self._on_error = callback

    def set_on_close(self, callback: Callable[[int], None]) -> None:
        self._on_close = callback

    def kill(self):
        self._process.terminate()


class AsyncioShellAdapter(IShellAdapter):
    """An adapter for shell command execution using asyncio."""

    async def _stream_reader(self, stream: asyncio.StreamReader, on_data: Callable[[str], None]):
        """Helper to read lines from a stream and invoke a callback."""
        while not stream.at_eof():
            line = await stream.readline()
            if line:
                on_data(line.decode('utf-8'))

    async def execute(self, command: str, working_dir: str, shell: str) -> IRunningProcess:
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=working_dir,
            executable=shell,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        running_process = AsyncioRunningProcess(process)

        # This task will complete when the process and all its output streams are closed.
        async def _manage_process():
            try:
                # Concurrently read stdout and stderr
                # Note: stdout and stderr are guaranteed to be non-None since we set PIPE
                if process.stdout is not None and process.stderr is not None:
                    await asyncio.gather(
                        self._stream_reader(process.stdout, running_process._on_data),
                        self._stream_reader(process.stderr, running_process._on_data)
                    )
                # Wait for the process to exit and get the code
                exit_code = await process.wait()
                running_process._on_close(exit_code)
            except Exception as e:
                running_process._on_error(e)

        asyncio.create_task(_manage_process())
        return running_process

    def get_system_shell(self) -> str:
        shell_path = os.environ.get("SHELL")
        if shell_path and os.path.exists(shell_path):
            return shell_path
        
        if os.name == 'nt':
            powershell_path = shutil.which('powershell')
            if powershell_path:
                return powershell_path
            return shutil.which('cmd') or 'cmd.exe'
            
        return '/bin/sh'