"""Tests for the Slack NestBot command."""

from unittest.mock import MagicMock, patch

import pytest

from apps.slack.blocks import markdown
from apps.slack.commands.nestbot import NestBot


class TestNestBotCommand:
    """Slack NestBot command tests."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.nestbot_cmd = NestBot()

    def test_command_name(self):
        """Should have correct command name."""
        assert self.nestbot_cmd.command_name == "/nestbot"

    @patch("apps.slack.common.handlers.calendar_events.get_setting_reminder_blocks")
    def test_render_setting_reminder_blocks_valid_args(self, mock_get_setting_reminder_blocks):
        """Test render_setting_reminder_blocks with valid arguments."""
        mock_get_setting_reminder_blocks.return_value = [markdown("Reminder set!")]
        command = {
            "text": "reminder set --channel C123456 --event_number 1 --minutes_before 10",
            "user_id": "U123456",
        }
        blocks = self.nestbot_cmd.render_blocks(command)
        assert blocks == [markdown("Reminder set!")]
        mock_get_setting_reminder_blocks.assert_called_once()

    @patch("apps.nest.utils.calendar_events.parse_reminder_args")
    def test_render_blocks_invalid_args(self, mock_parse_reminder_args):
        """Test render_blocks with invalid arguments."""
        mock_parse_reminder_args.side_effect = SystemExit
        command = {"text": "--invalid-arg", "user_id": "U123456"}
        blocks = self.nestbot_cmd.render_blocks(command)
        assert len(blocks) == 1
        assert (
            "*Invalid command format. Please check your input and try again.*"
            in blocks[0]["text"]["text"]
        )
        mock_parse_reminder_args.assert_called_once()

    @patch("apps.nest.utils.calendar_events.parse_cancel_reminder_args")
    @patch("apps.slack.common.handlers.calendar_events.get_cancel_reminder_blocks")
    def test_render_cancel_reminder_blocks_success(self, mock_get_blocks, mock_parse):
        """Should render cancel blocks successfully."""
        mock_args = MagicMock()
        mock_args.number = 4
        mock_parse.return_value = mock_args
        mock_blocks = ["block1", "block2"]
        mock_get_blocks.return_value = mock_blocks
        command = {"text": "reminder cancel --number 4", "user_id": "U12345"}
        blocks = self.nestbot_cmd.render_blocks(command)
        mock_parse.assert_called_once_with("reminder cancel --number 4")
        mock_get_blocks.assert_called_once_with(mock_args.number, "U12345")
        assert blocks == mock_blocks

    @patch("apps.nest.utils.calendar_events.parse_cancel_reminder_args")
    def test_render_cancel_reminder_blocks_invalid_args(self, mock_parse):
        """Should handle invalid cancel command arguments."""
        mock_parse.side_effect = SystemExit
        command = {"text": "--invalid-option", "user_id": "U12345"}
        blocks = self.nestbot_cmd.render_blocks(command)
        mock_parse.assert_called_once_with("--invalid-option")
        assert blocks == [
            markdown("*Invalid command format. Please check your input and try again.*")
        ]
