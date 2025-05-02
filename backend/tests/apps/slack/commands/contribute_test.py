from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.contribute import COMMAND, contribute_handler

GET_BLOCKS_PATH = "apps.slack.commands.contribute.get_blocks"
NO_ISSUES_TEXT = "*No issues found*"


@pytest.fixture(autouse=True)
def mock_get_absolute_url():
    with patch("apps.common.utils.get_absolute_url") as mock:
        mock.return_value = "http://example.com"
        yield mock


class TestContributeHandler:
    @pytest.fixture
    def mock_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture
    def mock_contribute_blocks(self):
        with patch(GET_BLOCKS_PATH) as mock:
            mock.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": NO_ISSUES_TEXT}}
            ]
            yield mock

    def test_handler_disabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = False

        contribute_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    def test_handler_default(self, mock_command, mock_client, mock_contribute_blocks):
        settings.SLACK_COMMANDS_ENABLED = True

        contribute_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        assert mock_contribute_blocks.call_count == 1
        assert mock_contribute_blocks.call_args.kwargs["search_query"] == ""

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)
        assert NO_ISSUES_TEXT in text

    def test_handler_with_search_term(self, mock_command, mock_client, mock_contribute_blocks):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "search term"

        contribute_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        assert mock_contribute_blocks.call_count == 1
        assert mock_contribute_blocks.call_args.kwargs["search_query"] == "search term"

    def test_handler_with_start_flag(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "--start"

        with patch(GET_BLOCKS_PATH) as mock_blocks:
            mock_blocks.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": NO_ISSUES_TEXT}}
            ]
            contribute_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)
        assert NO_ISSUES_TEXT in text

    def test_handler_with_advanced_flag(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "--advanced"

        with patch(GET_BLOCKS_PATH) as mock_blocks:
            mock_blocks.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": NO_ISSUES_TEXT}}
            ]
            contribute_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

    def test_handler_with_invalid_flag(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "--invalid"

        with patch(GET_BLOCKS_PATH) as mock_blocks:
            mock_blocks.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": NO_ISSUES_TEXT}}
            ]
            contribute_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

    def test_handler_with_help_flag(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "-h"

        with patch(GET_BLOCKS_PATH) as mock_blocks:
            mock_blocks.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": "Help information"}}
            ]
            contribute_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import contribute

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(contribute)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "contribute_handler"
