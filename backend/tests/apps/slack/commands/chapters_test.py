from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.chapters import Chapters


@pytest.fixture(autouse=True)
def mock_get_absolute_url():
    with patch("apps.common.utils.get_absolute_url") as mock:
        mock.return_value = "https://example.com"
        yield mock


@pytest.fixture(autouse=True)
def mock_active_chapters_count():
    with patch("apps.owasp.models.chapter.Chapter.active_chapters_count") as mock:
        mock.return_value = 100
        yield mock


class TestChaptersHandler:
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

    @pytest.fixture(autouse=True)
    def mock_get_chapters(self):
        with patch("apps.owasp.index.search.chapter.get_chapters") as mock:
            mock.return_value = {"hits": [], "nbPages": 1}
            yield mock

    @pytest.mark.parametrize(
        ("commands_enabled", "command_text", "expected_calls"),
        [
            (True, "", 1),
            (True, "search term", 1),
            (True, "-h", 1),
            (False, "", 0),
        ],
    )
    def test_chapters_handler(
        self, mock_client, mock_command, commands_enabled, command_text, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = command_text

        ack = MagicMock()
        Chapters().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()
        assert mock_client.chat_postMessage.call_count == expected_calls

    def test_chapters_handler_with_results(self, mock_get_chapters, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_chapters.return_value = {
            "hits": [
                {
                    "idx_name": "Test Chapter",
                    "idx_summary": "Test Summary",
                    "idx_url": "https://example.com",
                    "idx_leaders": ["Leader 1"],
                    "idx_country": "Test Country",
                    "idx_suggested_location": "Test Location",
                    "idx_region": "Test Region",
                    "idx_updated_at": "2024-01-01",
                }
            ],
            "nbPages": 1,
        }
        ack = MagicMock()
        Chapters().handler(ack=ack, command=mock_command, client=mock_client)

        ack.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert any("Test Chapter" in str(block) for block in blocks)
        assert any("Test Summary" in str(block) for block in blocks)
