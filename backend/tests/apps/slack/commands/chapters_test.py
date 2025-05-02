from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.chapters import COMMAND, chapters_handler
from apps.slack.common.constants import COMMAND_HELP

EXAMPLE_URL = "http://example.com"
TEST_CHAPTER_TEXT = "Test Chapter"
GET_BLOCKS_PATH = "apps.slack.common.handlers.chapters.get_blocks"


class TestChaptersHandler:
    @pytest.fixture(autouse=True)
    def mock_get_absolute_url(self):
        with patch("apps.common.utils.get_absolute_url") as mock:
            mock.return_value = EXAMPLE_URL
            yield mock

    @pytest.fixture(autouse=True)
    def mock_active_chapters_count(self):
        with patch("apps.owasp.models.chapter.Chapter.active_chapters_count") as mock:
            mock.return_value = 100
            yield mock

    @pytest.fixture
    def mock_command(self):
        return {"text": "", "user_id": "U123456"}

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture(autouse=True)
    def mock_get_blocks(self):
        with patch(GET_BLOCKS_PATH, autospec=True) as mock:
            mock.return_value = [
                {"type": "section", "text": {"type": "mrkdwn", "text": TEST_CHAPTER_TEXT}}
            ]
            yield mock

    @pytest.fixture(autouse=True)
    def mock_get_chapters(self):
        with patch("apps.owasp.api.search.chapter.get_chapters") as mock:
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
        ids=["enabled_empty", "enabled_search", "enabled_help", "disabled"],
    )
    def test_chapters_handler(
        self, mock_client, mock_command, commands_enabled, command_text, expected_calls
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_command["text"] = command_text

        chapters_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        assert mock_client.chat_postMessage.call_count == expected_calls

    def test_chapters_handler_with_results(self, mock_get_chapters, mock_client, mock_command):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_chapters.return_value = {
            "hits": [
                {
                    "idx_name": TEST_CHAPTER_TEXT,
                    "idx_summary": "Test Summary",
                    "idx_url": EXAMPLE_URL,
                    "idx_leaders": ["Leader 1"],
                    "idx_country": "Test Country",
                    "idx_suggested_location": "Test Location",
                    "idx_region": "Test Region",
                    "idx_updated_at": "2024-01-01",
                }
            ],
            "nbPages": 1,
        }

        chapters_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        assert mock_client.chat_postMessage.called

    @pytest.mark.parametrize("command_text", ["-h", "--help"], ids=["short_help", "long_help"])
    def test_chapters_handler_help(self, mock_client, mock_command, command_text):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = command_text

        chapters_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        assert any("Available Commands" in str(block) for block in blocks)

    @pytest.mark.parametrize(
        "command_text",
        ["", "test search", "-s", "--start"],
        ids=["empty", "search_term", "short_start", "long_start"],
    )
    def test_chapters_handler_search(
        self, mock_client, mock_command, mock_get_blocks, command_text
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_command["text"] = command_text

        with patch(
            GET_BLOCKS_PATH,
            return_value=mock_get_blocks.return_value,
        ):
            chapters_handler(ack=MagicMock(), command=mock_command, client=mock_client)

            if command_text in COMMAND_HELP:
                mock_get_blocks.assert_not_called()
            else:
                mock_client.chat_postMessage.assert_called_once()

    def test_command_registration(self):
        with patch("apps.slack.apps.SlackConfig.app") as mock_app:
            mock_command_decorator = MagicMock()
            mock_app.command.return_value = mock_command_decorator

            import importlib

            import apps.slack.commands.chapters

            importlib.reload(apps.slack.commands.chapters)

            mock_app.command.assert_called_once_with(COMMAND)
            assert mock_command_decorator.call_count == 1
