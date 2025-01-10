"""Test cases for committees command."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.committees import handler


class TestCommitteesHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture()
    def mock_committee(self):
        return {
            "idx_name": "Test Committee",
            "idx_summary": "Test committee summary",
            "idx_url": "http://example.com/committee/1",
            "idx_leaders": ["Leader A", "Leader B"],
        }

    @pytest.mark.parametrize(
        ("commands_enabled", "has_results", "expected_message"),
        [
            (False, True, None),
            (True, False, "No results found for"),
            (True, True, "Here are top available OWASP committees"),
        ],
    )
    @patch("apps.owasp.models.committee.Committee.active_committees_count")
    @patch("apps.owasp.api.search.committee.get_committees")
    def test_handler_responses(
        self,
        mock_get_committees,
        mock_active_committees_count,
        commands_enabled,
        has_results,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_committee,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_committees.return_value = {"hits": [mock_committee] if has_results else []}
        mock_active_committees_count.return_value = 42

        handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert any(expected_message in str(block) for block in blocks)
            if has_results:
                assert any(mock_committee["idx_name"] in str(block) for block in blocks)
                assert any(mock_committee["idx_url"] in str(block) for block in blocks)
                assert any(mock_committee["idx_summary"] in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("search_text", "expected_escaped"),
        [
            ("test <>&", "test &lt;&gt;&amp;"),
            ("normal search", "normal search"),
        ],
    )
    @patch("apps.owasp.models.committee.Committee.active_committees_count")
    @patch("apps.owasp.api.search.committee.get_committees")
    def test_handler_special_characters(
        self,
        mock_get_committees,
        mock_active_committees_count,
        search_text,
        expected_escaped,
        mock_slack_client,
    ):
        command = {"text": search_text, "user_id": "U123456"}
        mock_get_committees.return_value = {"hits": []}
        mock_active_committees_count.return_value = 42
        settings.SLACK_COMMANDS_ENABLED = True

        handler(ack=MagicMock(), command=command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert any(expected_escaped in str(block) for block in blocks)
