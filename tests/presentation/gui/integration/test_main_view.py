"""
Integration tests for the MainView.

These tests require wx.App to be running and test the actual wxPython widgets.
They verify that the UI components work correctly and integrate with the presenter.
"""
import pytest
import wx
from unittest.mock import Mock, AsyncMock


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
    return presenter


class TestMainViewCreation:
    """Test MainView instantiation and basic properties."""

    def test_main_view_can_be_created(self, wx_app, mock_presenter):
        """
        Test 1: MainView can be instantiated with a presenter.

        This is our first failing integration test - MainView doesn't exist yet.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        assert view is not None
        assert isinstance(view, wx.Frame)
        view.Destroy()

    def test_main_view_has_title(self, wx_app, mock_presenter):
        """
        Test 2: MainView has a proper window title.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        title = view.GetTitle()
        assert "Project Dashboard" in title or "Dashboard" in title
        view.Destroy()

    def test_main_view_has_menu_bar(self, wx_app, mock_presenter):
        """
        Test 3: MainView has a menu bar.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        menu_bar = view.GetMenuBar()
        assert menu_bar is not None
        assert isinstance(menu_bar, wx.MenuBar)
        view.Destroy()

    def test_main_view_has_file_menu(self, wx_app, mock_presenter):
        """
        Test 4: MainView has a File menu with Open Project option.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)
        menu_bar = view.GetMenuBar()

        # Find the File menu
        file_menu = None
        for i in range(menu_bar.GetMenuCount()):
            label = menu_bar.GetMenuLabelText(i)
            if "File" in label:
                file_menu = menu_bar.GetMenu(i)
                break

        assert file_menu is not None, "File menu not found"

        # Check for Open Project menu item
        has_open_project = False
        for item in file_menu.GetMenuItems():
            if "Open" in item.GetItemLabelText() or "Project" in item.GetItemLabelText():
                has_open_project = True
                break

        assert has_open_project, "Open Project menu item not found"
        view.Destroy()

    def test_main_view_has_status_bar(self, wx_app, mock_presenter):
        """
        Test 5: MainView has a status bar.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        status_bar = view.GetStatusBar()
        assert status_bar is not None
        assert isinstance(status_bar, wx.StatusBar)
        view.Destroy()


class TestMainViewInterface:
    """Test the view interface methods required by the presenter."""

    def test_set_project_name_updates_title(self, wx_app, mock_presenter):
        """
        Test 6: set_project_name() updates the window title.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        view.set_project_name("My Test Project")

        title = view.GetTitle()
        assert "My Test Project" in title
        view.Destroy()

    def test_set_status_updates_status_bar(self, wx_app, mock_presenter):
        """
        Test 7: set_status() updates the status bar text.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        view.set_status("Project loaded successfully")

        status_bar = view.GetStatusBar()
        status_text = status_bar.GetStatusText()
        assert "Project loaded successfully" in status_text
        view.Destroy()

    def test_show_error_displays_message_dialog(self, wx_app, mock_presenter, monkeypatch):
        """
        Test 8: show_error() displays an error message to the user.

        We'll mock wx.MessageBox to avoid blocking on dialog.
        """
        from src.presentation.gui.views.main_view import MainView

        # Mock wx.MessageBox to capture the call
        message_box_called = []
        def mock_message_box(message, caption, style, parent):
            message_box_called.append({
                'message': message,
                'caption': caption,
                'style': style
            })
            return wx.ID_OK

        monkeypatch.setattr(wx, 'MessageBox', mock_message_box)

        view = MainView(mock_presenter)
        view.show_error("An error occurred")

        assert len(message_box_called) == 1
        assert "An error occurred" in message_box_called[0]['message']
        assert message_box_called[0]['style'] & wx.ICON_ERROR
        view.Destroy()


class TestMainViewPresenterIntegration:
    """Test that the view properly integrates with the presenter."""

    def test_view_stores_presenter_reference(self, wx_app, mock_presenter):
        """
        Test 9: MainView maintains a reference to its presenter.
        """
        from src.presentation.gui.views.main_view import MainView

        view = MainView(mock_presenter)

        assert hasattr(view, 'presenter')
        assert view.presenter == mock_presenter
        view.Destroy()

    def test_open_project_menu_shows_directory_dialog(self, wx_app, mock_presenter, monkeypatch):
        """
        Test 10: Selecting "Open Project" from File menu shows a directory picker.

        We'll mock wx.DirDialog to avoid blocking on the dialog.
        """
        from src.presentation.gui.views.main_view import MainView

        # Mock wx.DirDialog
        dialog_shown = []
        class MockDirDialog:
            def __init__(self, parent, message, defaultPath, style):
                dialog_shown.append({
                    'message': message,
                    'defaultPath': defaultPath
                })

            def ShowModal(self):
                return wx.ID_CANCEL  # Simulate user canceling

            def GetPath(self):
                return "/test/path"

            def Destroy(self):
                pass

        monkeypatch.setattr('wx.DirDialog', MockDirDialog)

        view = MainView(mock_presenter)

        # Find and trigger the Open Project menu item
        menu_bar = view.GetMenuBar()
        for i in range(menu_bar.GetMenuCount()):
            label = menu_bar.GetMenuLabelText(i)
            if "File" in label:
                file_menu = menu_bar.GetMenu(i)
                for item in file_menu.GetMenuItems():
                    if "Open" in item.GetItemLabelText():
                        # Simulate menu selection
                        event = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, item.GetId())
                        view.ProcessEvent(event)
                        break
                break

        # Verify dialog was shown
        assert len(dialog_shown) >= 1, "Directory dialog was not shown"
        view.Destroy()
