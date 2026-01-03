"""
Unit tests for the DiscoveryService.
"""
import pytest
import json
from src.core.services import DiscoveryService
from tests.core.test_configuration_service import MockFileSystemAdapter # Re-use our mock

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_fs_adapter() -> MockFileSystemAdapter:
    return MockFileSystemAdapter()

@pytest.fixture
def discovery_service(mock_fs_adapter) -> DiscoveryService:
    return DiscoveryService(mock_fs_adapter)


async def test_discover_from_package_json_finds_targets(discovery_service, mock_fs_adapter):
    """
    Verify that the service correctly finds and parses a valid package.json.
    """
    project_root = "/fake/project"
    package_json_path = f"{project_root}/package.json"
    
    mock_package_json = {
        "name": "test-project",
        "scripts": {
            "start": "node index.js",
            "test": "jest"
        }
    }
    
    mock_fs_adapter.files[package_json_path] = json.dumps(mock_package_json)
    
    # Mock the find_files method to return our test file
    async def mock_find_files(pattern, root):
        if pattern == "**/package.json":
            return [package_json_path]
        return []
    mock_fs_adapter.find_files = mock_find_files

    targets = await discovery_service.discover_targets(project_root)

    assert len(targets) == 2
    assert targets[0].name == "start"
    assert targets[0].command == "npm run start"
    assert targets[0].source_file == package_json_path
    assert targets[1].name == "test"

async def test_discover_handles_no_package_json(discovery_service, mock_fs_adapter):
    """
    Verify that the service returns an empty list when no package.json is found.
    """
    project_root = "/fake/project"
    
    # Mock find_files to return nothing
    async def mock_find_files(pattern, root):
        return []
    mock_fs_adapter.find_files = mock_find_files

    targets = await discovery_service.discover_targets(project_root)
    assert len(targets) == 0

async def test_discover_handles_malformed_package_json(discovery_service, mock_fs_adapter):
    """
    Verify that the service gracefully handles a malformed package.json file.
    """
    project_root = "/fake/project"
    package_json_path = f"{project_root}/package.json"
    
    mock_fs_adapter.files[package_json_path] = "this is not valid json"
    
    async def mock_find_files(pattern, root):
        return [package_json_path]
    mock_fs_adapter.find_files = mock_find_files

    targets = await discovery_service.discover_targets(project_root)
    assert len(targets) == 0

async def test_discover_handles_package_json_with_no_scripts(discovery_service, mock_fs_adapter):
    """
    Verify that the service handles a package.json file that has no 'scripts' key.
    """
    project_root = "/fake/project"
    package_json_path = f"{project_root}/package.json"
    
    mock_package_json = {
        "name": "test-project-no-scripts"
    }
    
    mock_fs_adapter.files[package_json_path] = json.dumps(mock_package_json)
    
    async def mock_find_files(pattern, root):
        return [package_json_path]
    mock_fs_adapter.find_files = mock_find_files

    targets = await discovery_service.discover_targets(project_root)
    assert len(targets) == 0