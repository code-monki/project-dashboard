"""
Application entry point for the Project Dashboard GUI.

This module creates and configures the wxPython application, sets up
dependency injection for all services, and launches the main window.
"""
import wx
import asyncio
from src.infrastructure.adapters import (
    YamlConfigSerializer,
    AioFileSystemAdapter,
    AsyncioShellAdapter
)
from src.core.services import (
    ConfigurationService,
    DiscoveryService,
    ExecutionService,
    ProjectService
)
from src.presentation.gui.presenters.main_presenter import MainPresenter
from src.presentation.gui.views.main_view import MainView


class DashboardApp(wx.App):
    """
    Main application class for Project Dashboard.

    This class:
    1. Sets up all infrastructure adapters
    2. Initializes core services with dependency injection
    3. Creates the presenter and view (MVP pattern)
    4. Configures the asyncio event loop for async operations
    5. Shows the main window
    """

    def OnInit(self):
        """
        Initialize the application.

        This method is called by wxPython during app startup.
        It sets up all services and creates the main window.

        Returns:
            True if initialization was successful, False otherwise
        """
        # Setup asyncio event loop
        self._setup_event_loop()

        # Initialize infrastructure adapters
        self.fs_adapter = AioFileSystemAdapter()
        self.shell_adapter = AsyncioShellAdapter()
        self.serializer = YamlConfigSerializer()

        # Initialize core services
        self.config_service = ConfigurationService(
            self.fs_adapter,
            self.serializer
        )
        self.discovery_service = DiscoveryService(self.fs_adapter)
        self.execution_service = ExecutionService(self.shell_adapter)

        # Initialize project service (facade)
        self.project_service = ProjectService(
            self.config_service,
            self.discovery_service,
            self.execution_service
        )

        # Create presenter and view (MVP pattern)
        self.presenter = MainPresenter(self.project_service, None)
        self.main_view = MainView(self.presenter)

        # Connect presenter to view
        self.presenter.view = self.main_view

        # Show the main window
        self.main_view.Show()

        return True

    def _setup_event_loop(self):
        """
        Setup the asyncio event loop.

        This ensures async operations (like loading projects) work correctly
        with the wxPython event loop.
        """
        try:
            # Try to get the existing event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # If no loop exists, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # The event loop will be managed by asyncio.create_task() calls
        # from the view and presenter


def main():
    """
    Main entry point for the application.

    Creates the DashboardApp instance and starts the wxPython event loop.
    """
    app = DashboardApp(redirect=False)
    app.MainLoop()


if __name__ == '__main__':
    main()
