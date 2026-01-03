"""
MainPresenter - Implements the Presenter in the MVP pattern.

This presenter handles the business logic for the main application window,
coordinating between the view and the core services. It is fully testable
without requiring wx.App instantiation.
"""
from typing import Optional
from src.core.services import ProjectService


class MainPresenter:
    """
    Presenter for the main application window.

    Responsibilities:
    - Coordinate between the view and ProjectService
    - Handle user actions (load project, run targets, etc.)
    - Update the view based on service responses
    - Handle errors and display them to the user
    """

    def __init__(self, project_service: ProjectService, view):
        """
        Initialize the MainPresenter.

        Args:
            project_service: The ProjectService instance for core operations
            view: The view interface (implements set_project_name, set_status, show_error)
        """
        self.project_service = project_service
        self.view = view

    async def load_project(self, project_root: str) -> None:
        """
        Load a project from the specified root directory.

        This method:
        1. Calls the ProjectService to load the project
        2. Updates the view with the project name
        3. Updates the status bar with success message
        4. Handles any errors and displays them to the user

        Args:
            project_root: The absolute path to the project root directory
        """
        try:
            # Load the project via the service
            config = await self.project_service.load_project(project_root)

            # Update the view with the project name
            if config:
                self.view.set_project_name(config.project_name)
                self.view.set_status(f"Project '{config.project_name}' loaded successfully")

        except Exception as e:
            # Handle errors and display to user
            error_message = f"Failed to load project: {str(e)}"
            self.view.show_error(error_message)

    def get_project_name(self) -> Optional[str]:
        """
        Get the currently loaded project name.

        Returns:
            The project name if a project is loaded, None otherwise
        """
        config = self.project_service.get_config()
        if config:
            return config.project_name
        return None
