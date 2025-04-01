from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.common.constants import NL, OWASP_NEWS_URL
from apps.slack.commands.news import news_handler


class TestNewsHandler:
    @pytest.fixture
    def mock_command(self):
        return {"user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(("commands_enabled", "expected_calls"), [(False, 0), (True, 1)])
    def test_news_handler_disabled_enabled(
        self, mock_client, mock_command, commands_enabled, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
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
            news_handler(ack=ack, command=mock_command, client=mock_client)
            ack.assert_called_once()
            assert mock_client.chat_postMessage.call_count == expected_calls
            if commands_enabled:
                mock_client.conversations_open.assert_called_once_with(
                    users=mock_command["user_id"]
                )
                blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
                if mock_get_news_data.return_value:
                    assert blocks[0]["text"]["text"] == f"*:newspaper: Latest OWASP news:*{NL}"
                    news_blocks = blocks[1 : 1 + len(mock_get_news_data.return_value)]
                    for item, block in zip(mock_get_news_data.return_value, news_blocks):
                        expected = f"  • *<{item['url']}|{item['title']}>* by {item['author']}"
                        assert block["text"]["text"] == expected
                    assert blocks[-2]["type"] == "divider"
                    footer = blocks[-1]["text"]["text"]
                    expected_footer = (
                        f"Please visit <{OWASP_NEWS_URL}|OWASP news> page for more "
                        f"information.{NL}"
                    )
                    assert footer == expected_footer
                else:
                    expected_warning = (
                        ":warning: *Failed to fetch OWASP news. Please try again later.*"
                    )
                    assert blocks[0]["text"]["text"] == expected_warning

    @patch("apps.slack.commands.news.get_news_data")
    def test_news_handler_no_items(self, mock_get_news_data, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_news_data.return_value = []
        ack = MagicMock()
        news_handler(ack=ack, command=mock_command, client=mock_client)
        ack.assert_called_once()
        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) == 1
        expected_warning = ":warning: *Failed to fetch OWASP news. Please try again later.*"
        assert blocks[0]["text"]["text"] == expected_warning
