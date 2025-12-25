"""Tests for the nest_update_badges management command."""

from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import SimpleTestCase


class TestNestUpdateBadgesCommand(SimpleTestCase):
    """Tests for the nest_update_badges management command."""

    @patch("apps.nest.management.commands.nest_update_badges.Command.BADGE_HANDLERS")
    def test_sync_runs_all_handlers(self, mock_handlers_dict):
        """Test command runs process() for all handlers when no arg provided."""
        mock_staff_handler_class = MagicMock()
        mock_staff_handler_class.name = "OWASP Staff"
        mock_leader_handler_class = MagicMock()
        mock_leader_handler_class.name = "OWASP Project Leader"
        mock_handlers_dict.values.return_value = [
            mock_staff_handler_class,
            mock_leader_handler_class,
        ]
        mock_handlers_dict.keys.return_value = ["staff", "leader"]

        out = StringIO()
        call_command("nest_update_badges", stdout=out)

        mock_staff_handler_class.return_value.process.assert_called_once()
        mock_leader_handler_class.return_value.process.assert_called_once()

        output = out.getvalue()
        assert "Processing badge: OWASP Staff" in output
        assert "User badges sync completed" in output

    @patch("apps.nest.management.commands.nest_update_badges.Command.BADGE_HANDLERS")
    def test_sync_specific_handler(self, mock_handlers_dict):
        """Test that passing --handler runs only that specific handler."""
        mock_staff_handler_class = MagicMock()
        mock_staff_handler_class.name = "OWASP Staff"
        mock_handlers_dict.keys.return_value = ["staff"]

        def get_handler(key):
            return mock_staff_handler_class if key == "staff" else None

        mock_handlers_dict.__getitem__.side_effect = get_handler
        out = StringIO()
        call_command("nest_update_badges", "--handler=staff", stdout=out)
        mock_staff_handler_class.return_value.process.assert_called_once()
        assert "Syncing specific badge: staff" in out.getvalue()

    @patch("apps.nest.management.commands.nest_update_badges.Command.BADGE_HANDLERS")
    def test_sync_handles_exceptions_gracefully(self, mock_handlers_dict):
        """Test that if one handler fails, the command logs it and continues."""
        mock_staff_handler_class = MagicMock()
        mock_staff_handler_class.name = "OWASP Staff"

        mock_leader_handler_class = MagicMock()
        mock_leader_handler_class.name = "OWASP Project Leader"

        mock_staff_handler_class.return_value.process.side_effect = Exception("Database Error")
        mock_handlers_dict.values.return_value = [
            mock_staff_handler_class,
            mock_leader_handler_class,
        ]

        mock_handlers_dict.keys.return_value = ["staff", "leader"]
        out = StringIO()
        call_command("nest_update_badges", stdout=out)
        mock_staff_handler_class.return_value.process.assert_called_once()
        mock_leader_handler_class.return_value.process.assert_called_once()
        output = out.getvalue()
        assert "Failed to update OWASP Staff" in output
        assert "Processing badge: OWASP Project Leader" in output

    @patch("apps.nest.management.commands.nest_update_badges.logger")
    @patch("apps.nest.management.commands.nest_update_badges.Command.BADGE_HANDLERS")
    def test_logs_exception(self, mock_handlers_dict, mock_logger):
        """Test that exceptions are logged with stack traces."""
        mock_staff_handler_class = MagicMock()
        mock_staff_handler_class.name = "OWASP Staff"
        mock_staff_handler_class.return_value.process.side_effect = Exception("Critical Failure")
        mock_handlers_dict.values.return_value = [mock_staff_handler_class]
        mock_handlers_dict.keys.return_value = ["staff"]
        call_command("nest_update_badges", stdout=StringIO())
        mock_logger.exception.assert_called_with("Error processing badge %s", "OWASP Staff")
