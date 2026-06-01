"""Tests for the restore_backup Django management command."""

from contextlib import suppress
from unittest.mock import MagicMock, patch

from django.core.management.base import BaseCommand

from apps.common.management.commands.restore_backup import Command


class TestRestoreBackupCommand:
    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("apps.common.management.commands.restore_backup.call_command")
    @patch("apps.common.management.commands.restore_backup.transaction.atomic")
    def test_handle_success(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test successful execution of the restore_backup command."""
        mock_atomic.return_value.__enter__ = MagicMock()
        mock_atomic.return_value.__exit__ = MagicMock()
        mock_unregister.return_value = None
        mock_register.return_value = None
        mock_call_command.return_value = None

        command = Command()
        command.handle()

        mock_unregister.assert_called_once()
        mock_atomic.assert_called_once()
        mock_call_command.assert_called_once_with("loaddata", "data/backup.json.gz", "-v", "3")
        mock_register.assert_called_once()

        mock_atomic.return_value.__enter__.assert_called_once()
        mock_atomic.return_value.__exit__.assert_called_once()

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("apps.common.management.commands.restore_backup.call_command")
    @patch("apps.common.management.commands.restore_backup.transaction.atomic")
    def test_handle_with_exception_during_loaddata(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test that indexing is re-enabled even if data loading fails."""
        mock_atomic.return_value.__enter__ = MagicMock()
        mock_atomic.return_value.__exit__ = MagicMock()
        mock_unregister.return_value = None
        mock_register.return_value = None
        mock_call_command.side_effect = Exception("Data loading failed")

        command = Command()
        with suppress(Exception):
            command.handle()

        mock_unregister.assert_called_once()
        mock_register.assert_called_once()

        mock_atomic.return_value.__enter__.assert_called_once()
        mock_atomic.return_value.__exit__.assert_called_once()

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("apps.common.management.commands.restore_backup.call_command")
    @patch("apps.common.management.commands.restore_backup.transaction.atomic")
    def test_handle_with_exception_during_unregister_indexing(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test behavior when call_command fails."""
        mock_call_command.side_effect = Exception("Call command failed")

        command = Command()
        with suppress(Exception):
            command.handle()

        mock_unregister.assert_called_once()

        mock_atomic.assert_called_once()
        mock_call_command.assert_called_once_with("loaddata", "data/backup.json.gz", "-v", "3")
        mock_register.assert_called_once()

    @patch("apps.core.utils.index.DisableIndexing.unregister_indexes")
    @patch("apps.core.utils.index.DisableIndexing.register_indexes")
    @patch("apps.common.management.commands.restore_backup.call_command")
    @patch("apps.common.management.commands.restore_backup.transaction.atomic")
    def test_handle_with_exception_during_register_indexing(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test behavior when register_indexes fails."""
        mock_atomic.return_value.__enter__ = MagicMock()
        mock_atomic.return_value.__exit__ = MagicMock()
        mock_call_command.side_effect = Exception("Register indexing failed")

        command = Command()
        with suppress(Exception):
            command.handle()

        mock_unregister.assert_called_once()
        mock_atomic.assert_called_once()
        mock_call_command.assert_called_once_with("loaddata", "data/backup.json.gz", "-v", "3")
        mock_register.assert_called_once()

        mock_atomic.return_value.__enter__.assert_called_once()
        mock_atomic.return_value.__exit__.assert_called_once()

    def test_command_help_text(self):
        """Test that the command has the correct help text."""
        command = Command()
        assert command.help == "Restore OWASP Nest data from a backup."

    def test_command_inheritance(self):
        """Test that the command inherits from BaseCommand."""
        command = Command()

        assert isinstance(command, BaseCommand)
