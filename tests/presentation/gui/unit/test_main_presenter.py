"""
Unit tests for the MainPresenter.

These tests verify the presenter logic in isolation without requiring
a wx.App instance. All dependencies are mocked.
"""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from src.core.models import ProjectConfig, Target
from src.core.services import ProjectService


class TestMainPresenter:
    """Unit tests for MainPresenter following TDD approach."""

    @pytest.fixture
    def mock_project_service(self):
        """Create a mock ProjectService."""
        service = Mock(spec=ProjectService)
        service.load_project = AsyncMock()
        service.get_config = Mock()
        return service

    @pytest.fixture
    def mock_view(self):
        """Create a mock view interface."""
        view = Mock()
        view.set_project_name = Mock()
        view.set_status = Mock()
        view.show_error = Mock()
        return view

    def test_presenter_can_be_instantiated(self, mock_project_service, mock_view):
        """
        Test 1: MainPresenter can be instantiated with a ProjectService and View.

        This is our first failing test - MainPresenter doesn't exist yet.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        presenter = MainPresenter(mock_project_service, mock_view)

        assert presenter is not None
        assert presenter.project_service == mock_project_service
        assert presenter.view == mock_view

    @pytest.mark.asyncio
    async def test_load_project_calls_service(self, mock_project_service, mock_view):
        """
        Test 2: load_project() method calls ProjectService.load_project().

        This verifies the presenter delegates to the service layer.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        project_root = "/test/project"
        mock_config = ProjectConfig(project_name="Test Project", targets=[])
        mock_project_service.load_project.return_value = mock_config

        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        await presenter.load_project(project_root)

        # Verify
        mock_project_service.load_project.assert_called_once_with(project_root)

    @pytest.mark.asyncio
    async def test_load_project_updates_view_with_project_name(self, mock_project_service, mock_view):
        """
        Test 3: After loading project, the view is updated with the project name.

        This verifies the presenter updates the view after successful load.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        project_root = "/test/project"
        mock_config = ProjectConfig(project_name="My Awesome Project", targets=[])
        mock_project_service.load_project.return_value = mock_config
        mock_project_service.get_config.return_value = mock_config

        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        await presenter.load_project(project_root)

        # Verify
        mock_view.set_project_name.assert_called_once_with("My Awesome Project")

    @pytest.mark.asyncio
    async def test_load_project_updates_status_on_success(self, mock_project_service, mock_view):
        """
        Test 4: Status bar is updated with success message after loading.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        project_root = "/test/project"
        mock_config = ProjectConfig(project_name="Test Project", targets=[])
        mock_project_service.load_project.return_value = mock_config

        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        await presenter.load_project(project_root)

        # Verify
        mock_view.set_status.assert_called()
        status_message = mock_view.set_status.call_args[0][0]
        assert "loaded" in status_message.lower() or "success" in status_message.lower()

    @pytest.mark.asyncio
    async def test_load_project_shows_error_on_exception(self, mock_project_service, mock_view):
        """
        Test 5: Errors during project loading are displayed to the user.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        project_root = "/test/project"
        mock_project_service.load_project.side_effect = Exception("Failed to load project")

        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        await presenter.load_project(project_root)

        # Verify
        mock_view.show_error.assert_called_once()
        error_message = mock_view.show_error.call_args[0][0]
        assert "failed" in error_message.lower() or "error" in error_message.lower()

    def test_get_project_name_returns_none_when_no_project_loaded(self, mock_project_service, mock_view):
        """
        Test 6: get_project_name() returns None when no project is loaded.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        mock_project_service.get_config.return_value = None
        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        project_name = presenter.get_project_name()

        # Verify
        assert project_name is None

    def test_get_project_name_returns_name_when_project_loaded(self, mock_project_service, mock_view):
        """
        Test 7: get_project_name() returns the project name when loaded.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        mock_config = ProjectConfig(project_name="Test Project", targets=[])
        mock_project_service.get_config.return_value = mock_config
        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        project_name = presenter.get_project_name()

        # Verify
        assert project_name == "Test Project"

    def test_get_targets_returns_empty_list_when_no_project_loaded(self, mock_project_service, mock_view):
        """
        Test 8: get_targets() returns empty list when no project is loaded.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        mock_project_service.get_config.return_value = None
        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        targets = presenter.get_targets()

        # Verify
        assert targets == []

    def test_get_targets_returns_target_list_when_project_loaded(self, mock_project_service, mock_view):
        """
        Test 9: get_targets() returns the list of targets when project is loaded.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        target1 = Target(name="build", command="npm run build", source_file="package.json")
        target2 = Target(name="test", command="npm test", source_file="package.json")
        mock_config = ProjectConfig(project_name="Test Project", targets=[target1, target2])
        mock_project_service.get_config.return_value = mock_config
        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        targets = presenter.get_targets()

        # Verify
        assert len(targets) == 2
        assert targets[0].name == "build"
        assert targets[1].name == "test"

    @pytest.mark.asyncio
    async def test_load_project_updates_target_list_in_view(self, mock_project_service, mock_view):
        """
        Test 10: After loading project, the view's target list is updated.
        """
        from src.presentation.gui.presenters.main_presenter import MainPresenter

        # Setup
        project_root = "/test/project"
        target1 = Target(name="build", command="npm run build", source_file="package.json")
        target2 = Target(name="test", command="npm test", source_file="package.json")
        mock_config = ProjectConfig(project_name="Test Project", targets=[target1, target2])
        mock_project_service.load_project.return_value = mock_config
        mock_project_service.get_config.return_value = mock_config
        mock_view.update_target_list = Mock()

        presenter = MainPresenter(mock_project_service, mock_view)

        # Execute
        await presenter.load_project(project_root)

        # Verify
        mock_view.update_target_list.assert_called_once()
        call_args = mock_view.update_target_list.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0].name == "build"
        assert call_args[1].name == "test"
