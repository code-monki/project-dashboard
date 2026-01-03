"""
Unit tests for the ConfigurationService.
"""
import pytest
from unittest.mock import MagicMock
from src.core.services import ConfigurationService, CONFIG_FILE_NAME
from src.core.models import ProjectConfig

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

class MockFileSystemAdapter:
    """A mock implementation of IFileSystemAdapter for testing."""
    def __init__(self):
        self.files = {}

    async def file_exists(self, path: str) -> bool:
        return path in self.files

    async def read_file(self, path: str) -> str:
        return self.files.get(path, "")

    async def write_file(self, path: str, content: str) -> None:
        self.files[path] = content

    async def find_files(self, pattern: str, root_dir: str) -> list[str]:
        return [] # Not needed for this test

class MockSerializer:
    """A mock implementation of IConfigSerializer for testing."""
    def serialize(self, config: ProjectConfig) -> str:
        # A simple mock serialization
        return f"project_name: {config.project_name}"

    def deserialize(self, data: str) -> dict:
        # A simple mock deserialization
        name = data.split(": ")[1]
        return {"project_name": name, "targets": [], "groups": []}


@pytest.fixture
def mock_fs_adapter() -> MockFileSystemAdapter:
    return MockFileSystemAdapter()

@pytest.fixture
def mock_serializer() -> MockSerializer:
    return MockSerializer()

@pytest.fixture
def config_service(mock_fs_adapter, mock_serializer) -> ConfigurationService:
    return ConfigurationService(mock_fs_adapter, mock_serializer)


async def test_load_config_returns_none_if_file_not_found(config_service):
    """
    Verify that load_config returns None when the config file doesn't exist.
    """
    config = await config_service.load_config("/fake/project")
    assert config is None

async def test_load_config_returns_config_if_file_exists(config_service, mock_fs_adapter):
    """
    Verify that load_config correctly deserializes and returns a ProjectConfig object.
    """
    project_root = "/fake/project"
    config_path = f"{project_root}/{CONFIG_FILE_NAME}"
    await mock_fs_adapter.write_file(config_path, "project_name: Test Project")

    config = await config_service.load_config(project_root)

    assert config is not None
    assert isinstance(config, ProjectConfig)
    assert config.project_name == "Test Project"

async def test_save_config_writes_serialized_data_to_file(config_service, mock_fs_adapter):
    """
    Verify that save_config correctly serializes and writes the config to a file.
    """
    project_root = "/fake/project"
    config_path = f"{project_root}/{CONFIG_FILE_NAME}"
    config_to_save = ProjectConfig(project_name="My New Project")

    await config_service.save_config(project_root, config_to_save)

    assert await mock_fs_adapter.file_exists(config_path)
    file_content = await mock_fs_adapter.read_file(config_path)
    assert file_content == "project_name: My New Project"
