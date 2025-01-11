from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.owasp import handler


@pytest.fixture()
def mock_ack():
    return MagicMock()


@pytest.fixture()
def mock_client():
    return MagicMock()


@pytest.fixture()
def mock_command():
    return {"text": "", "user_id": "U12345"}


class TestOwaspHandler:
    @patch("apps.slack.commands.owasp.markdown")
    def test_help_command(self, mock_markdown, mock_ack, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = ""

        mock_markdown.return_value = {"text": "HELP_MESSAGE"}

        mock_client.conversations_open.return_value = {"channel": {"id": "C12345"}}

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        _, kwargs = mock_client.chat_postMessage.call_args
        assert kwargs["blocks"][0]["text"] == "HELP_MESSAGE"

    def test_disabled_slack_commands(self, mock_ack, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = False

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.commands.contribute.handler")
    def test_contribute_handler(
        self, mock_contribute_handler, mock_ack, mock_client, mock_command
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "contribute"

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_contribute_handler.assert_called_once_with(mock_ack, mock_command, mock_client)

    @patch("apps.slack.commands.gsoc.handler")
    def test_gsoc_handler(self, mock_gsoc_handler, mock_ack, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "gsoc"

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_gsoc_handler.assert_called_once_with(mock_ack, mock_command, mock_client)

    @patch("apps.slack.commands.chapters.handler")
    def test_chapters_handler(self, mock_chapters_handler, mock_ack, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "chapters"

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_chapters_handler.assert_called_once_with(mock_ack, mock_command, mock_client)

    @patch("apps.slack.commands.projects.handler")
    def test_projects_handler(self, mock_projects_handler, mock_ack, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "projects"

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_projects_handler.assert_called_once_with(mock_ack, mock_command, mock_client)

    @patch("apps.slack.commands.committees.handler")
    def test_committees_handler(
        self, mock_committees_handler, mock_ack, mock_client, mock_command
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "committees"

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_committees_handler.assert_called_once_with(mock_ack, mock_command, mock_client)

    @patch("apps.slack.commands.owasp.markdown")
    def test_unsupported_command(self, mock_markdown, mock_ack, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = "unsupported_command"

        mock_markdown.return_value = {"text": "NOT_SUPPORTED_MESSAGE"}

        mock_client.conversations_open.return_value = {"channel": {"id": "C12345"}}

        handler(mock_ack, mock_command, mock_client)

        mock_ack.assert_called_once()
        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        _, kwargs = mock_client.chat_postMessage.call_args
        assert kwargs["blocks"][0]["text"] == "NOT_SUPPORTED_MESSAGE"
