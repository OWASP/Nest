from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import OWASP_NEWS_URL
from apps.owasp.utils.news import get_news_data
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

    @pytest.mark.parametrize(
        ("commands_enabled", "expected_calls"),
        [
            (False, 0),
            (True, 1),
        ],
    )
    def test_news_handler_disabled_enabled(
        self, mock_client, mock_command, commands_enabled, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        # Clear cache before test
        get_news_data.cache_clear()
        # Patch where it's imported and used
        with patch("apps.slack.commands.news.get_news_data") as mock_get_news_data:
            mock_get_news_data.return_value = (
                [
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
                if commands_enabled
                else []
            )
            ack = MagicMock()
            News().handler(ack=ack, command=mock_command, client=mock_client)

            ack.assert_called_once()
            assert mock_client.chat_postMessage.call_count == expected_calls

            if commands_enabled:
                mock_client.conversations_open.assert_called_once_with(
                    users=mock_command["user_id"]
                )
                blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
                if mock_get_news_data.return_value:
                    # Check that the header is present
                    assert "*:newspaper: Latest OWASP news:*" in blocks[0]["text"]["text"]
                    # Check that news items are present
                    news_text = blocks[0]["text"]["text"]
                    for item in mock_get_news_data.return_value:
                        assert item["title"] in news_text
                        assert item["author"] in news_text
                        assert item["url"] in news_text
                    # Check that the footer is present in the same block
                    assert "Please visit" in news_text
                    assert OWASP_NEWS_URL in news_text
                    assert "OWASP news" in news_text
                else:
                    expected_warning = (
                        ":warning: *Failed to fetch OWASP news. Please try again later.*"
                    )
                    assert blocks[0]["text"]["text"] == expected_warning

    @patch("apps.slack.commands.news.get_news_data")
    def test_news_handler_no_items(self, mock_get_news_data, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        # Clear cache before test
        get_news_data.cache_clear()
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
