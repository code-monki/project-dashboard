"""
Unit tests for the ProjectService facade.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.core.services import ProjectService, ConfigurationService, DiscoveryService, ExecutionService
from src.core.models import ProjectConfig, Target

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_config_service():
    return Mock(spec=ConfigurationService)

@pytest.fixture
def mock_discovery_service():
    return Mock(spec=DiscoveryService)

@pytest.fixture
def mock_execution_service():
    service = Mock(spec=ExecutionService)
    # Mock the nested adapter for get_system_shell
    service._shell_adapter = Mock()
    service._shell_adapter.get_system_shell.return_value = "/bin/zsh"
    return service

@pytest.fixture
def project_service(mock_config_service, mock_discovery_service, mock_execution_service):
    return ProjectService(mock_config_service, mock_discovery_service, mock_execution_service)


async def test_load_project_from_existing_config(project_service, mock_config_service, mock_discovery_service):
    """
    Verify that if a config exists, it's loaded and discovery is not run.
    """
    project_root = "/fake/project"
    mock_config = ProjectConfig(project_name="Existing Project")
    
    # Configure the mock to return a config
    mock_config_service.load_config = AsyncMock(return_value=mock_config)
    mock_discovery_service.discover_targets = AsyncMock()

    config = await project_service.load_project(project_root)

    mock_config_service.load_config.assert_called_once_with(project_root)
    mock_discovery_service.discover_targets.assert_not_called()
    assert config == mock_config
    assert project_service.get_config() == mock_config

async def test_load_project_creates_new_config_if_none_exists(project_service, mock_config_service, mock_discovery_service):
    """
    Verify that if no config exists, targets are discovered and a new config is created and saved.
    """
    project_root = "/fake/project"
    discovered_target = Target(name="test", command="npm test", source_file="package.json")

    # Configure mocks
    mock_config_service.load_config = AsyncMock(return_value=None)
    mock_config_service.save_config = AsyncMock()
    mock_discovery_service.discover_targets = AsyncMock(return_value=[discovered_target])

    config = await project_service.load_project(project_root)

    mock_config_service.load_config.assert_called_once_with(project_root)
    mock_discovery_service.discover_targets.assert_called_once_with(project_root)
    
    # Check that save_config was called with the correct data
    mock_config_service.save_config.assert_called_once()
    saved_config_arg = mock_config_service.save_config.call_args[0][1]
    assert saved_config_arg.project_name == "project"
    assert saved_config_arg.targets == [discovered_target]

    assert config is not None
    assert config.targets[0].name == "test"

async def test_run_target_executes_correct_target(project_service, mock_execution_service):
    """
    Verify that run_target finds the correct target and calls the execution service.
    """
    target_to_run = Target(id="abc-123", name="test", command="npm test", source_file="package.json")
    # Manually set up the service's internal state for the test
    project_service._config = ProjectConfig(project_name="Test", targets=[target_to_run])
    project_service._project_root = "/fake/project"
    mock_execution_service.run_target.return_value = 999

    pid = project_service.run_target("abc-123")

    assert pid == 999
    mock_execution_service.run_target.assert_called_once_with(target_to_run, "/fake/project", "/bin/zsh")

async def test_run_target_raises_error_if_not_found(project_service):
    """
    Verify that run_target raises a ValueError for an unknown target ID.
    """
    project_service._config = ProjectConfig(project_name="Test", targets=[])
    project_service._project_root = "/fake/project"

    with pytest.raises(ValueError, match="Target with ID 'xyz-789' not found."):
        project_service.run_target("xyz-789")