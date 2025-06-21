"""Tests for the restore_backup Django management command."""

from contextlib import suppress
from unittest.mock import MagicMock, patch

from django.core.management.base import BaseCommand

from apps.common.management.commands.restore_backup import Command


class TestRestoreBackupCommand:
    @patch("apps.common.management.commands.restore_backup.unregister_indexes")
    @patch("apps.common.management.commands.restore_backup.register_indexes")
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

    @patch("apps.common.management.commands.restore_backup.unregister_indexes")
    @patch("apps.common.management.commands.restore_backup.register_indexes")
    @patch("apps.common.management.commands.restore_backup.call_command")
    @patch("apps.common.management.commands.restore_backup.transaction.atomic")
    def test_handle_with_exception_during_loaddata(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test that indexing is re-enabled even if loaddata fails."""
        mock_atomic.return_value.__enter__ = MagicMock()
        mock_atomic.return_value.__exit__ = MagicMock()
        mock_unregister.return_value = None
        mock_register.return_value = None
        mock_call_command.side_effect = Exception("Loaddata failed")

        command = Command()
        with suppress(Exception):
            command.handle()

        mock_unregister.assert_called_once()

        mock_atomic.return_value.__enter__.assert_called_once()
        mock_atomic.return_value.__exit__.assert_called_once()

        mock_register.assert_called_once()

    @patch("apps.common.management.commands.restore_backup.unregister_indexes")
    @patch("apps.common.management.commands.restore_backup.register_indexes")
    @patch("apps.common.management.commands.restore_backup.call_command")
    @patch("apps.common.management.commands.restore_backup.transaction.atomic")
    def test_handle_with_exception_during_unregister(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test behavior when unregister_indexes fails."""
        mock_unregister.side_effect = Exception("Unregister failed")
        mock_register.return_value = None

        command = Command()
        with suppress(Exception):
            command.handle()

        mock_unregister.assert_called_once()

        mock_atomic.assert_not_called()
        mock_call_command.assert_not_called()
        mock_register.assert_not_called()

    @patch("apps.common.management.commands.restore_backup.unregister_indexes")
    @patch("apps.common.management.commands.restore_backup.register_indexes")
    @patch("apps.common.management.commands.restore_backup.call_command")
    @patch("apps.common.management.commands.restore_backup.transaction.atomic")
    def test_handle_with_exception_during_register(
        self,
        mock_atomic,
        mock_call_command,
        mock_register,
        mock_unregister,
    ):
        """Test behavior when register_indexes fails."""
        mock_atomic.return_value.__enter__ = MagicMock()
        mock_atomic.return_value.__exit__ = MagicMock()
        mock_unregister.return_value = None
        mock_register.side_effect = Exception("Register failed")
        mock_call_command.return_value = None

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
