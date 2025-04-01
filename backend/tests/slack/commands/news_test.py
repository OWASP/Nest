from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.news import COMMAND, news_handler


class TestNewsHandler:
    @pytest.fixture()
    def mock_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture(autouse=True)
    def mock_news_data(self):
        with patch("apps.slack.commands.news.get_news_data") as mock:
            mock.return_value = [
                {"title": "News 1", "author": "Author 1", "url": "https://example.com/news1"},
                {"title": "News 2", "author": "Author 2", "url": "https://example.com/news2"},
            ]
            yield mock

    def test_handler_disabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = False

        news_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    def test_handler_with_news_data(self, mock_command, mock_client, mock_news_data):
        settings.SLACK_COMMANDS_ENABLED = True

        news_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "Latest OWASP news" in text
        assert "News 1" in text
        assert "News 2" in text
        assert "Author 1" in text
        assert "Author 2" in text

    def test_handler_no_news_data(self, mock_command, mock_client, mock_news_data):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_news_data.return_value = []

        news_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "Failed to fetch OWASP news" in text

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import news

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(news)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "news_handler"
