from unittest.mock import MagicMock, patch

import pytest

from apps.slack.management.commands.run_slack_bot import Command


def test_help_text():
    command = Command()
    assert command.help == "Runs Slack bot application."


@patch("apps.slack.management.commands.run_slack_bot.SocketModeHandler")
@patch("apps.slack.management.commands.run_slack_bot.settings")
def test_handle_with_valid_token(mock_settings, mock_socket_handler):
    mock_settings.SLACK_APP_TOKEN = "xapp-valid-token"
    mock_handler = MagicMock()
    mock_socket_handler.return_value = mock_handler

    command = Command()
    command.handle()

    mock_socket_handler.assert_called_once()
    mock_handler.start.assert_called_once()


@patch("apps.slack.management.commands.run_slack_bot.SocketModeHandler")
@patch("apps.slack.management.commands.run_slack_bot.settings")
def test_handle_with_none_token(mock_settings, mock_socket_handler):
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
def test_handle_with_socket_error(mock_logger, mock_settings, mock_socket_handler):
    mock_settings.SLACK_APP_TOKEN = "xapp-valid-token"
    mock_handler = MagicMock()
    mock_handler.start.side_effect = Exception("Socket error")
    mock_socket_handler.return_value = mock_handler

    command = Command()
    with pytest.raises(Exception):
        command.handle()


@patch("apps.slack.management.commands.run_slack_bot.SocketModeHandler")
@patch("apps.slack.management.commands.run_slack_bot.settings")
@patch("apps.slack.management.commands.run_slack_bot.SlackConfig")
def test_handle_app_initialization(mock_slack_config, mock_settings, mock_socket_handler):
    mock_settings.SLACK_APP_TOKEN = "xapp-valid-token"
    mock_app = MagicMock()
    mock_slack_config.app = mock_app
    mock_handler = MagicMock()
    mock_socket_handler.return_value = mock_handler

    command = Command()
    command.handle()

    mock_socket_handler.assert_called_once_with(mock_app, "xapp-valid-token")
    mock_handler.start.assert_called_once()
