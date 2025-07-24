import contextlib
from unittest.mock import MagicMock, patch

from apps.common.management.commands.load_data import Command


class TestLoadDataCommand:
    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("apps.common.management.commands.load_data.call_command")
    @patch("apps.common.management.commands.load_data.transaction.atomic")
    def test_handle(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        mock_model = MagicMock()
        mock_app_config = MagicMock()
        mock_app_config.get_models.return_value = [mock_model]

        mock_atomic.return_value.__enter__ = MagicMock()
        mock_atomic.return_value.__exit__ = MagicMock()

        mock_unregister.return_value = None
        mock_register.return_value = None

        command = Command()
        command.handle()

        mock_unregister.assert_called_once()
        mock_register.assert_called_once()

        mock_call_command.assert_called_once_with("loaddata", "data/nest.json.gz", "-v", "3")

        mock_atomic.assert_called_once()

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("apps.common.management.commands.load_data.call_command")
    @patch("apps.common.management.commands.load_data.transaction.atomic")
    def test_handle_with_exception_during_call_command(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test that indexing is re-enabled even if call_command fails."""
        mock_call_command.side_effect = Exception("Call command failed")

        command = Command()
        with patch("contextlib.suppress") as mock_suppress:
            mock_suppress.return_value.__enter__ = MagicMock()
            mock_suppress.return_value.__exit__ = MagicMock()

            with contextlib.suppress(Exception):
                command.handle()

        mock_unregister.assert_called_once()
        mock_register.assert_called_once()

        mock_atomic.assert_called_once()
