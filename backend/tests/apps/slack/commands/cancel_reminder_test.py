"""Test cases for Slack cancel reminder command."""

from unittest.mock import MagicMock, patch

from apps.slack.blocks import markdown
from apps.slack.commands.cancel_reminder import CancelReminder


class TestCancelReminder:
    """Slack cancel reminder command tests."""

    def test_command_name(self):
        """Should have correct command name."""
        assert CancelReminder().command_name == "/cancel-reminder"

    @patch("apps.nest.utils.calendar_events.parse_cancel_reminder_args")
    @patch("apps.slack.common.handlers.calendar_events.get_cancel_reminder_blocks")
    def test_render_blocks_success(self, mock_get_blocks, mock_parse):
        """Should render blocks successfully."""
        mock_args = MagicMock()
        mock_args.number = 4
        mock_parse.return_value = mock_args
        mock_blocks = ["block1", "block2"]
        mock_get_blocks.return_value = mock_blocks
        command = {"text": "--number 4", "user_id": "U12345"}
        blocks = CancelReminder().render_blocks(command)
        mock_parse.assert_called_once_with("--number 4")
        mock_get_blocks.assert_called_once_with(mock_args.number, "U12345")
        assert blocks == mock_blocks

    @patch("apps.nest.utils.calendar_events.parse_cancel_reminder_args")
    def test_render_blocks_invalid_args(self, mock_parse):
        """Should handle invalid command arguments."""
        mock_parse.side_effect = SystemExit
        command = {"text": "--invalid-option", "user_id": "U12345"}
        blocks = CancelReminder().render_blocks(command)
        mock_parse.assert_called_once_with("--invalid-option")
        assert blocks == [
            markdown("*Invalid command arguments. Please check your input and try again.*")
        ]
