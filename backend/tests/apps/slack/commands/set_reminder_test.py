"""Test cases for set_reminder command."""

from unittest.mock import patch

from apps.slack.blocks import markdown
from apps.slack.commands.set_reminder import SetReminder


class TestSetReminderCommand:
    @patch("apps.slack.commands.set_reminder.get_setting_reminder_blocks")
    def test_render_blocks_valid_args(self, mock_get_setting_reminder_blocks):
        """Test render_blocks with valid arguments."""
        mock_get_setting_reminder_blocks.return_value = [markdown("Reminder set!")]
        command = {
            "text": "--channel C123456 --event_number 1 --minutes_before 10",
            "user_id": "U123456",
        }
        set_reminder_cmd = SetReminder()
        blocks = set_reminder_cmd.render_blocks(command)
        assert blocks == [markdown("Reminder set!")]
        mock_get_setting_reminder_blocks.assert_called_once()

    @patch("apps.nest.utils.calendar_events.parse_reminder_args")
    def test_render_blocks_invalid_args(self, mock_parse_reminder_args):
        """Test render_blocks with invalid arguments."""
        mock_parse_reminder_args.side_effect = SystemExit()
        command = {"text": "--invalid-arg", "user_id": "U123456"}
        set_reminder_cmd = SetReminder()
        blocks = set_reminder_cmd.render_blocks(command)
        assert len(blocks) == 1
        assert (
            "*Invalid command format. Please check your input and try again.*"
            in blocks[0]["text"]["text"]
        )
        mock_parse_reminder_args.assert_called_once()
