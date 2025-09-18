"""Test cases for Calendar Events Slack Scheduler."""

from unittest.mock import MagicMock, patch

from apps.nest.schedulers.calendar_events.slack import SlackScheduler


class TestSlackScheduler:
    """Test cases for the SlackScheduler class."""

    @patch("apps.nest.schedulers.calendar_events.slack.SlackConfig")
    def test_send_message(self, mock_slack_config):
        """Test sending a message via Slack."""
        mock_slack_config.app = MagicMock()
        mock_client = mock_slack_config.app.client
        SlackScheduler.send_message("Test Message", "C123456")

        mock_client.chat_postMessage.assert_called_once_with(
            channel="C123456",
            text="Test Message",
        )

    @patch("apps.nest.schedulers.calendar_events.slack.SlackScheduler.send_message")
    @patch("apps.nest.schedulers.calendar_events.slack.update_reminder_schedule_date")
    def test_send_and_update(self, mock_update_reminder_schedule_date, mock_send_message):
        """Test sending a message and updating it via Slack."""
        mock_reminder_schedule = MagicMock()
        SlackScheduler.send_and_update("Test Message", "C123456", mock_reminder_schedule)

        mock_send_message.assert_called_once_with("Test Message", "C123456")
        mock_update_reminder_schedule_date.assert_called_once_with(mock_reminder_schedule)
