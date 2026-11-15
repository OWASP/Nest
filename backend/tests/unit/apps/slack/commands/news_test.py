from unittest.mock import MagicMock, patch

import pytest
from django.test import override_settings

from apps.common.constants import OWASP_NEWS_URL
from apps.slack.commands.news import News


class TestNewsCommand:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @patch("apps.slack.commands.news.get_news_data")
    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_news_handler(self, mock_get_news_data, mock_client, mock_command):
        mock_get_news_data.return_value = [
            {
                "url": "https://example.com/news1",
                "title": "News One",
                "author": "Author A",
            },
            {
                "url": "https://example.com/news2",
                "title": "News Two",
                "author": "Author B",
            },
        ]
        ack = MagicMock()
        News().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == 1

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert "*:newspaper: Latest OWASP news:*" in blocks[0]["text"]["text"]
        news_text = blocks[0]["text"]["text"]
        for item in mock_get_news_data.return_value:
            assert item["title"] in news_text
            assert item["author"] in news_text
            assert item["url"] in news_text
        assert "Please visit" in news_text
        assert OWASP_NEWS_URL in news_text
        assert "OWASP news" in news_text

    @override_settings(SLACK_COMMANDS_ENABLED=False)
    def test_news_handler_when_commands_disabled(self, mock_client, mock_command):
        ack = MagicMock()
        News().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.commands.news.get_news_data")
    @override_settings(SLACK_COMMANDS_ENABLED=True)
    def test_news_handler_no_items(self, mock_get_news_data, mock_client, mock_command):
        mock_get_news_data.return_value = []
        ack = MagicMock()
        News().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]

        assert len(blocks) == 2
        assert (
            blocks[0]["text"]["text"]
            == ":warning: *Failed to fetch OWASP news. Please try again later.*"
        )
        assert blocks[1]["type"] == "section"
        assert blocks[1]["text"]["type"] == "mrkdwn"
        assert "💬 You can share feedback" in blocks[1]["text"]["text"]
