"""Tests for core index utilities."""

from unittest.mock import MagicMock, patch

from apps.core.utils.index import DisableIndexing


class TestDisableIndexing:
    """Test the DisableIndexing context manager."""

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    def test_disable_indexing_context_manager(self, mock_register, mock_unregister):
        """Test that the context manager properly disables and re-enables indexing."""
        with DisableIndexing():
            mock_unregister.assert_called_once()
            mock_register.assert_not_called()

        mock_register.assert_called_once()

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("django.apps.apps.get_app_config")
    def test_disable_indexing_with_custom_app_names(
        self, mock_get_app_config, mock_register, mock_unregister
    ):
        """Test that the context manager works with custom app names."""
        custom_apps = ("custom_app", "another_app")

        mock_app_config = MagicMock()
        mock_app_config.get_models.return_value = []
        mock_get_app_config.return_value = mock_app_config

        with DisableIndexing(custom_apps):
            mock_unregister.assert_called_once()
            mock_register.assert_not_called()

        mock_register.assert_called_once()
