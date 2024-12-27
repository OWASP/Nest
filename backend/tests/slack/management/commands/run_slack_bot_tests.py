from unittest.mock import MagicMock, patch

import pytest

from apps.slack.management.commands.run_slack_bot import Command
from tests.common.constants import TEST_SLACK_TOKEN


class TestSlackBotCommand:
    def test_help_text(self):
        command = Command()
        assert command.help == "Runs Slack bot application."

    @patch("apps.slack.management.commands.run_slack_bot.SocketModeHandler")
    @patch("apps.slack.management.commands.run_slack_bot.settings")
    def test_handle_with_valid_token(self, mock_settings, mock_socket_handler):
        mock_settings.SLACK_APP_TOKEN = TEST_SLACK_TOKEN
        mock_settings.SLACK_CONFIGURATION = "Local"
        mock_handler = MagicMock()
        mock_socket_handler.return_value = mock_handler

        command = Command()
        command.handle()

        mock_socket_handler.assert_called_once()
        mock_handler.start.assert_called_once()

    @patch("apps.slack.management.commands.run_slack_bot.SocketModeHandler")
    @patch("apps.slack.management.commands.run_slack_bot.settings")
    def test_handle_with_none_token(self, mock_settings, mock_socket_handler):
        mock_settings.SLACK_APP_TOKEN = "None"
        mock_handler = MagicMock()
        mock_socket_handler.return_value = mock_handler

        command = Command()
        command.handle()

        mock_socket_handler.assert_not_called()
        mock_handler.start.assert_not_called()

    @patch("apps.slack.management.commands.run_slack_bot.SocketModeHandler")
    @patch("apps.slack.management.commands.run_slack_bot.settings")
    @patch("apps.slack.management.commands.run_slack_bot.logger")
    def test_handle_with_socket_error(self, mock_logger, mock_settings, mock_socket_handler):
        mock_settings.SLACK_APP_TOKEN = TEST_SLACK_TOKEN
        mock_settings.SLACK_CONFIGURATION = "Local"
        mock_handler = MagicMock()
        mock_handler.start.side_effect = ConnectionError("Socket error")
        mock_socket_handler.return_value = mock_handler

        mock_logger.warning.assert_not_called()
        command = Command()
        with pytest.raises(ConnectionError, match="Socket error"):
            command.handle()

    @pytest.mark.parametrize(
        ("token", "should_start"),
        [
            (TEST_SLACK_TOKEN, True),
            ("None", False),
        ],
    )
    @patch("apps.slack.management.commands.run_slack_bot.SocketModeHandler")
    @patch("apps.slack.management.commands.run_slack_bot.settings")
    @patch("apps.slack.management.commands.run_slack_bot.SlackConfig")
    def test_handle_app_initialization(
        self, mock_slack_config, mock_settings, mock_socket_handler, token, should_start
    ):
        mock_settings.SLACK_APP_TOKEN = token
        mock_settings.SLACK_CONFIGURATION = "Local"
        mock_app = MagicMock()
        mock_slack_config.app = mock_app
        mock_handler = MagicMock()
        mock_socket_handler.return_value = mock_handler

        command = Command()
        command.handle()

        if should_start:
            mock_socket_handler.assert_called_once_with(mock_app, token)
            mock_handler.start.assert_called_once()
        else:
            mock_socket_handler.assert_not_called()
            mock_handler.start.assert_not_called()
