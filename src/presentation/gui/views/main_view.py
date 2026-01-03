"""
MainView - The View component in the MVP pattern.

This view implements the wxPython GUI for the main application window.
It is "dumb" and delegates all business logic to the MainPresenter.
"""
import wx
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.presentation.gui.presenters.main_presenter import MainPresenter


class MainView(wx.Frame):
    """
    Main application window using wxPython.

    This view implements the interface expected by MainPresenter:
    - set_project_name(name: str) -> None
    - set_status(message: str) -> None
    - show_error(message: str) -> None

    The view is responsible only for displaying information and
    forwarding user actions to the presenter.
    """

    def __init__(self, presenter: 'MainPresenter', parent=None):
        """
        Initialize the main application window.

        Args:
            presenter: The MainPresenter instance that handles business logic
            parent: Optional parent window (default: None)
        """
        super().__init__(
            parent,
            title="Project Dashboard",
            size=(800, 600)
        )

        self.presenter = presenter

        # Create UI components
        self._create_menu_bar()
        self._create_status_bar()

        # Center the window on screen
        self.Centre()

    def _create_menu_bar(self) -> None:
        """Create the menu bar with File menu."""
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()

        # Open Project menu item
        open_project_item = file_menu.Append(
            wx.ID_OPEN,
            "&Open Project...\tCtrl+O",
            "Open a project directory"
        )
        self.Bind(wx.EVT_MENU, self._on_open_project, open_project_item)

        # Exit menu item
        exit_item = file_menu.Append(
            wx.ID_EXIT,
            "E&xit\tCtrl+Q",
            "Exit the application"
        )
        self.Bind(wx.EVT_MENU, self._on_exit, exit_item)

        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        status_bar = self.CreateStatusBar()
        status_bar.SetStatusText("Ready")

    def _on_open_project(self, event: wx.Event) -> None:
        """
        Handle the Open Project menu selection.

        Shows a directory picker and loads the selected project.
        """
        dialog = wx.DirDialog(
            self,
            "Choose a project directory",
            "",
            wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST
        )

        if dialog.ShowModal() == wx.ID_OK:
            project_path = dialog.GetPath()
            # Call presenter asynchronously
            asyncio.create_task(self.presenter.load_project(project_path))

        dialog.Destroy()

    def _on_exit(self, event: wx.Event) -> None:
        """Handle the Exit menu selection."""
        self.Close(True)

    # View Interface Methods (called by presenter)

    def set_project_name(self, name: str) -> None:
        """
        Update the window title with the project name.

        Args:
            name: The project name to display
        """
        self.SetTitle(f"Project Dashboard - {name}")

    def set_status(self, message: str) -> None:
        """
        Update the status bar with a message.

        Args:
            message: The status message to display
        """
        status_bar = self.GetStatusBar()
        if status_bar:
            status_bar.SetStatusText(message)

    def show_error(self, message: str) -> None:
        """
        Display an error message to the user.

        Args:
            message: The error message to display
        """
        wx.MessageBox(
            message,
            "Error",
            wx.OK | wx.ICON_ERROR,
            self
        )
