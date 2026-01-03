"""
Integration tests for target list display functionality.

These tests verify that targets are displayed correctly in the UI
and that users can interact with the target list.
"""
import pytest
import wx
from unittest.mock import Mock, AsyncMock
from src.core.models import Target, ProjectConfig


@pytest.fixture(scope="module")
def wx_app():
    """Create a wx.App instance for the test session."""
    app = wx.App(False)
    yield app
    app.Destroy()


@pytest.fixture
def mock_presenter():
    """Create a mock presenter for testing view in isolation."""
    presenter = Mock()
    presenter.load_project = AsyncMock()
    presenter.get_project_name = Mock(return_value=None)
    presenter.get_targets = Mock(return_value=[])
    return presenter


@pytest.fixture
def sample_targets():
    """Create sample targets for testing."""
    return [
        Target(name="build", command="npm run build", source_file="package.json"),
        Target(name="test", command="npm test", source_file="package.json"),
        Target(name="lint", command="npm run lint", source_file="package.json")
    ]


class TestTargetListUI:
    """Test the target list UI component in MainView."""

    def test_main_view_has_target_list_control(self, wx_app, mock_presenter):
        """
        Test 1: MainView contains a list control for displaying targets.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        # Verify list control exists
        assert hasattr(view, 'target_list')
        assert isinstance(view.target_list, wx.ListCtrl)

        view.Destroy()

    def test_target_list_has_correct_columns(self, wx_app, mock_presenter):
        """
        Test 2: Target list has columns for Name, Command, and Source File.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        # Verify columns
        assert view.target_list.GetColumnCount() >= 3

        # Check column headers
        col0_text = view.target_list.GetColumn(0).GetText()
        col1_text = view.target_list.GetColumn(1).GetText()
        col2_text = view.target_list.GetColumn(2).GetText()

        assert "Name" in col0_text or "Target" in col0_text
        assert "Command" in col1_text
        assert "Source" in col2_text or "File" in col2_text

        view.Destroy()

    def test_update_target_list_populates_items(self, wx_app, mock_presenter, sample_targets):
        """
        Test 3: update_target_list() method populates the list with targets.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        # Update with sample targets
        view.update_target_list(sample_targets)

        # Verify items were added
        assert view.target_list.GetItemCount() == 3

        # Verify first target details
        assert view.target_list.GetItemText(0, 0) == "build"
        assert "npm run build" in view.target_list.GetItemText(0, 1)
        assert "package.json" in view.target_list.GetItemText(0, 2)

        view.Destroy()

    def test_update_target_list_clears_previous_items(self, wx_app, mock_presenter, sample_targets):
        """
        Test 4: update_target_list() clears previous items before adding new ones.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        # Add targets first time
        view.update_target_list(sample_targets)
        assert view.target_list.GetItemCount() == 3

        # Update with fewer targets
        new_targets = sample_targets[:1]
        view.update_target_list(new_targets)

        # Verify only new targets are shown
        assert view.target_list.GetItemCount() == 1
        assert view.target_list.GetItemText(0, 0) == "build"

        view.Destroy()

    def test_update_target_list_with_empty_list(self, wx_app, mock_presenter):
        """
        Test 5: update_target_list() with empty list clears the control.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        # Add some targets first
        targets = [Target(name="test", command="test cmd", source_file="test.txt")]
        view.update_target_list(targets)
        assert view.target_list.GetItemCount() == 1

        # Clear with empty list
        view.update_target_list([])

        # Verify list is empty
        assert view.target_list.GetItemCount() == 0

        view.Destroy()

    def test_target_list_selection_tracking(self, wx_app, mock_presenter, sample_targets):
        """
        Test 6: View tracks which target is currently selected.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)
        view.update_target_list(sample_targets)

        # Simulate selecting the second item
        view.target_list.Select(1)

        # Verify selection
        selected_index = view.target_list.GetFirstSelected()
        assert selected_index == 1

        view.Destroy()

    def test_get_selected_target_returns_none_when_nothing_selected(self, wx_app, mock_presenter, sample_targets):
        """
        Test 7: get_selected_target() returns None when no target is selected.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)
        view.update_target_list(sample_targets)

        # No selection made
        selected = view.get_selected_target()

        assert selected is None

        view.Destroy()

    def test_get_selected_target_returns_target_when_selected(self, wx_app, mock_presenter, sample_targets):
        """
        Test 8: get_selected_target() returns the selected Target object.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)
        view.update_target_list(sample_targets)

        # Select the second item (index 1 = "test")
        view.target_list.Select(1)

        selected = view.get_selected_target()

        assert selected is not None
        assert selected.name == "test"
        assert selected.command == "npm test"

        view.Destroy()
