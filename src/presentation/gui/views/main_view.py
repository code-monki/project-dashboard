"""
MainView - The View component in the MVP pattern.

This view implements the wxPython GUI for the main application window.
It is "dumb" and delegates all business logic to the MainPresenter.
"""
import wx
import asyncio
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from src.presentation.gui.presenters.main_presenter import MainPresenter

from src.core.models import Target


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

        # Store targets for selection tracking
        self._targets: List[Target] = []

        # Create UI components
        self._create_menu_bar()
        self._create_main_panel()
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

    def _create_main_panel(self) -> None:
        """Create the main panel with target list."""
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create target list control
        self.target_list = wx.ListCtrl(
            panel,
            style=wx.LC_REPORT | wx.LC_SINGLE_SEL
        )

        # Add columns
        self.target_list.AppendColumn("Name", width=150)
        self.target_list.AppendColumn("Command", width=400)
        self.target_list.AppendColumn("Source File", width=200)

        # Add to sizer
        sizer.Add(self.target_list, 1, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)

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

    def update_target_list(self, targets: List[Target]) -> None:
        """
        Update the target list with new targets.

        Args:
            targets: List of Target objects to display
        """
        # Store targets for selection tracking
        self._targets = targets

        # Clear existing items
        self.target_list.DeleteAllItems()

        # Add new items
        for target in targets:
            index = self.target_list.InsertItem(self.target_list.GetItemCount(), target.name)
            self.target_list.SetItem(index, 1, target.command)
            self.target_list.SetItem(index, 2, target.source_file)

    def get_selected_target(self) -> Optional[Target]:
        """
        Get the currently selected target.

        Returns:
            The selected Target object, or None if nothing is selected
        """
        selected_index = self.target_list.GetFirstSelected()
        if selected_index == -1:
            return None

        if 0 <= selected_index < len(self._targets):
            return self._targets[selected_index]

        return None
