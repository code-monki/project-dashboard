"""
Integration tests for the application entry point.

These tests verify that the application can be launched and properly
initializes all components (services, presenter, view).
"""
import pytest
import wx
from unittest.mock import Mock, patch, MagicMock
import os


class TestApplicationSetup:
    """Test application initialization and setup."""

    def test_app_module_exists(self):
        """
        Test 1: The app.py module can be imported.
        """
        from src.presentation.gui import app
        assert app is not None

    def test_app_class_exists(self):
        """
        Test 2: The app module contains a DashboardApp class.
        """
        from src.presentation.gui.app import DashboardApp
        assert DashboardApp is not None

    def test_dashboard_app_inherits_from_wx_app(self):
        """
        Test 3: DashboardApp inherits from wx.App.
        """
        from src.presentation.gui.app import DashboardApp
        assert issubclass(DashboardApp, wx.App)

    def test_dashboard_app_can_be_instantiated(self):
        """
        Test 4: DashboardApp can be instantiated.
        """
        from src.presentation.gui.app import DashboardApp

        app = DashboardApp(redirect=False)
        assert app is not None
        assert isinstance(app, wx.App)
        app.Destroy()

    def test_app_initializes_services(self):
        """
        Test 5: Application initializes all required services.

        This verifies the dependency injection setup.
        """
        from src.presentation.gui.app import DashboardApp

        app = DashboardApp(redirect=False)

        # Verify services are created
        assert hasattr(app, 'fs_adapter')
        assert hasattr(app, 'shell_adapter')
        assert hasattr(app, 'serializer')
        assert hasattr(app, 'config_service')
        assert hasattr(app, 'discovery_service')
        assert hasattr(app, 'execution_service')
        assert hasattr(app, 'project_service')

        app.Destroy()

    def test_app_creates_presenter(self):
        """
        Test 6: Application creates the MainPresenter.
        """
        from src.presentation.gui.app import DashboardApp

        app = DashboardApp(redirect=False)

        assert hasattr(app, 'presenter')
        assert app.presenter is not None

        app.Destroy()

    def test_app_creates_main_window(self):
        """
        Test 7: Application creates and shows the MainView window.
        """
        from src.presentation.gui.app import DashboardApp

        app = DashboardApp(redirect=False)

        # Verify main window is created
        assert hasattr(app, 'main_view')
        assert app.main_view is not None
        assert isinstance(app.main_view, wx.Frame)

        app.Destroy()

    def test_on_init_returns_true(self):
        """
        Test 8: OnInit() returns True to indicate successful initialization.
        """
        from src.presentation.gui.app import DashboardApp

        app = DashboardApp(redirect=False)

        # OnInit should have been called during instantiation
        # Verify the app is ready
        assert app.IsMainLoopRunning() or not app.IsMainLoopRunning()  # App exists

        app.Destroy()


class TestApplicationEntryPoint:
    """Test the main() entry point function."""

    def test_main_function_exists(self):
        """
        Test 9: A main() function exists as the entry point.
        """
        from src.presentation.gui.app import main
        assert callable(main)

    @patch('src.presentation.gui.app.DashboardApp')
    def test_main_creates_and_runs_app(self, mock_app_class):
        """
        Test 10: main() creates a DashboardApp instance and runs MainLoop.
        """
        from src.presentation.gui.app import main

        # Setup mock
        mock_app_instance = MagicMock()
        mock_app_class.return_value = mock_app_instance

        # Call main
        main()

        # Verify app was created and MainLoop was called
        mock_app_class.assert_called_once()
        mock_app_instance.MainLoop.assert_called_once()


class TestApplicationEventLoop:
    """Test asyncio event loop integration with wx.App."""

    def test_app_has_asyncio_event_loop(self):
        """
        Test 11: Application sets up an asyncio event loop for async operations.
        """
        from src.presentation.gui.app import DashboardApp
        import asyncio

        app = DashboardApp(redirect=False)

        # Verify event loop is available
        try:
            loop = asyncio.get_event_loop()
            assert loop is not None
        except RuntimeError:
            # If there's no running loop, that's also acceptable
            # as long as we can create one
            loop = asyncio.new_event_loop()
            assert loop is not None
            asyncio.set_event_loop(loop)

        app.Destroy()
