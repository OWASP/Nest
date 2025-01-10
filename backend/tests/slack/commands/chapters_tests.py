"""Test cases for chapters command."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.chapters import handler


class TestChaptersHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "text": "test chapter",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture()
    def mock_chapter(self):
        return {
            "idx_name": "Test Chapter",
            "idx_summary": "Test chapter summary",
            "idx_url": "http://example.com/chapter/1",
            "idx_leaders": ["Leader A", "Leader B"],
            "idx_region": "Test Region",
            "idx_country": "Test Country",
        }

    @pytest.mark.parametrize(
        ("commands_enabled", "has_results", "expected_message"),
        [
            (False, True, None),
            (True, False, "No results found for"),
            (True, True, "Here are top 10 OWASP chapters"),
        ],
    )
    @patch("apps.owasp.models.chapter.Chapter.active_chapters_count")
    @patch("apps.owasp.api.search.chapter.get_chapters")
    def test_handler_responses(
        self,
        mock_get_chapters,
        mock_active_chapters_count,
        commands_enabled,
        has_results,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_chapter,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_chapters.return_value = {"hits": [mock_chapter] if has_results else []}
        mock_active_chapters_count.return_value = 42

        handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert any(expected_message in str(block) for block in blocks)
            if has_results:
                assert any(mock_chapter["idx_name"] in str(block) for block in blocks)
                assert any(mock_chapter["idx_url"] in str(block) for block in blocks)
                assert any(mock_chapter["idx_summary"] in str(block) for block in blocks)

    def test_help_command(self, mock_slack_client):
        command = {"text": "--help", "user_id": "U123456"}
        settings.SLACK_COMMANDS_ENABLED = True

        handler(ack=MagicMock(), command=command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert any("Available Commands" in str(block) for block in blocks)
        assert any("/chapters [search term]" in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("search_text", "expected_escaped"),
        [
            ("test <>&", "test &lt;&gt;&amp;"),
            ("normal search", "normal search"),
        ],
    )
    @patch("apps.owasp.models.chapter.Chapter.active_chapters_count")
    @patch("apps.owasp.api.search.chapter.get_chapters")
    def test_handler_special_characters(
        self,
        mock_get_chapters,
        mock_active_chapters_count,
        search_text,
        expected_escaped,
        mock_slack_client,
    ):
        command = {"text": search_text, "user_id": "U123456"}
        mock_get_chapters.return_value = {"hits": []}
        mock_active_chapters_count.return_value = 42
        settings.SLACK_COMMANDS_ENABLED = True

        handler(ack=MagicMock(), command=command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert any(expected_escaped in str(block) for block in blocks)
