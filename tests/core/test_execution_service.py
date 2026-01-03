"""
Unit tests for the ExecutionService.
"""
import pytest
from unittest.mock import Mock
from src.core.services import ExecutionService
from src.core.models import Target

class MockRunningProcess:
    """A mock implementation of IRunningProcess for testing."""
    def __init__(self, pid: int):
        self.pid = pid
        self._on_close_callback = None
        self.kill_called = False

    def set_on_data(self, callback): pass
    def set_on_error(self, callback): pass
    def set_on_close(self, callback): self._on_close_callback = callback
    def kill(self):
        self.kill_called = True
        if self._on_close_callback:
            self._on_close_callback(self.pid) # Simulate process closing after kill

@pytest.fixture
def mock_shell_adapter():
    adapter = Mock()
    # Configure the 'execute' method to return a mock process
    adapter.execute.side_effect = lambda command, working_dir, shell: MockRunningProcess(pid=123)
    return adapter

@pytest.fixture
def execution_service(mock_shell_adapter):
    return ExecutionService(mock_shell_adapter)

def test_run_target_executes_command_and_tracks_process(execution_service, mock_shell_adapter):
    """Verify that run_target executes a command and tracks its process."""
    target = Target(name="test", command="echo 'hello'", source_file="test.sh")
    
    pid = execution_service.run_target(target, "/fake/project", "/bin/bash")

    assert pid == 123
    mock_shell_adapter.execute.assert_called_once_with("echo 'hello'", "/fake/project", "/bin/bash")
    assert execution_service.get_running_processes() == [123]

def test_cancel_target_kills_process_and_removes_from_tracking(execution_service):
    """Verify that cancel_target calls kill() and the process is removed."""
    target = Target(name="test", command="sleep 10", source_file="test.sh")
    pid = execution_service.run_target(target, "/fake/project", "/bin/bash")

    assert execution_service.get_running_processes() == [123]
    
    # Get the mock process object to check if kill() was called
    # This is a bit of a test smell, but necessary to check the interaction
    process = execution_service._running_processes[pid]

    execution_service.cancel_target(pid)

    assert process.kill_called is True
    assert execution_service.get_running_processes() == []

def test_get_running_processes_returns_correct_pids(execution_service, mock_shell_adapter):
    """Verify that get_running_processes returns a list of active PIDs."""
    # Configure the mock to return different PIDs on subsequent calls
    mock_shell_adapter.execute.side_effect = [MockRunningProcess(pid=101), MockRunningProcess(pid=202)]

    target1 = Target(name="test1", command="cmd1", source_file="test.sh")
    target2 = Target(name="test2", command="cmd2", source_file="test.sh")

    pid1 = execution_service.run_target(target1, "/fake", "/bin/sh")
    pid2 = execution_service.run_target(target2, "/fake", "/bin/sh")

    running_pids = execution_service.get_running_processes()
    assert len(running_pids) == 2
    assert 101 in running_pids
    assert 202 in running_pids