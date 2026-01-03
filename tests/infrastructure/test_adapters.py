"""
Integration tests for the infrastructure adapters.
These tests perform real I/O operations.
"""
import pytest
from src.infrastructure.adapters import YamlConfigSerializer, AioFileSystemAdapter
from src.core.models import ProjectConfig, Target

@pytest.fixture
def serializer():
    return YamlConfigSerializer()

@pytest.fixture
def fs_adapter():
    return AioFileSystemAdapter()

def test_yaml_serializer_cycle(serializer):
    """Test that serializing and then deserializing returns the original data structure."""
    target = Target(name="build", command="make build", source_file="Makefile")
    config = ProjectConfig(project_name="Test Project", targets=[target])

    serialized_data = serializer.serialize(config)
    deserialized_data = serializer.deserialize(serialized_data)

    assert deserialized_data['project_name'] == "Test Project"
    assert deserialized_data['targets'][0]['name'] == "build"

async def test_fs_adapter_write_read_cycle(fs_adapter, tmp_path):
    """Test writing a file and then reading it back."""
    test_file = tmp_path / "test.txt"
    content = "Hello, world!"

    await fs_adapter.write_file(str(test_file), content)
    read_content = await fs_adapter.read_file(str(test_file))

    assert read_content == content

async def test_fs_adapter_file_exists(fs_adapter, tmp_path):
    """Test the file_exists method."""
    existing_file = tmp_path / "exists.txt"
    non_existing_file = tmp_path / "does_not_exist.txt"
    await fs_adapter.write_file(str(existing_file), "data")

    assert await fs_adapter.file_exists(str(existing_file)) is True
    assert await fs_adapter.file_exists(str(non_existing_file)) is False

async def test_fs_adapter_find_files(fs_adapter, tmp_path):
    """Test the find_files method."""
    # Create a nested structure
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "package.json").touch()
    (tmp_path / "package.json").touch()

    found_files = await fs_adapter.find_files("**/package.json", str(tmp_path))

    assert len(found_files) == 2
    assert str(tmp_path / "package.json") in found_files
    assert str(tmp_path / "sub" / "package.json") in found_files