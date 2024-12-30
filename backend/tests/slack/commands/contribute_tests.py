from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.utils.text import Truncator

from apps.slack.commands.contribute import (
    COMMAND_START,
    SUMMARY_TRUNCATION_LIMIT,
    TITLE_TRUNCATION_LIMIT,
    handler,
)
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE


class TestContributeHandler:
    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "text": "python",
            "user_id": "U123456",
        }

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture()
    def mock_issue(self):
        return {
            "idx_project_name": "Test Project",
            "idx_summary": "Test Summary",
            "idx_title": "Test Title",
            "idx_url": "http://example.com/issue/1",
        }

    @pytest.mark.parametrize(
        ("command_enabled", "has_results", "expected_message"),
        [
            (True, True, "Here are top 10 most relevant issues"),
            (True, False, "No results found for"),
            (False, True, None),
        ],
    )
    @patch("apps.owasp.api.search.issue.get_issues")
    def test_handler_results(
        self,
        mock_get_issues,
        command_enabled,
        has_results,
        expected_message,
        mock_slack_client,
        mock_slack_command,
        mock_issue,
    ):
        settings.SLACK_COMMANDS_ENABLED = command_enabled
        mock_get_issues.return_value = {"hits": [mock_issue] if has_results else []}

        handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if command_enabled:
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
            assert any(expected_message in str(block) for block in blocks)
            if has_results:
                assert any(mock_issue["idx_title"] in str(block) for block in blocks)
        else:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()

    @pytest.mark.parametrize(
        ("title_length", "summary_length", "should_truncate"),
        [
            (TITLE_TRUNCATION_LIMIT + 10, SUMMARY_TRUNCATION_LIMIT + 10, True),
            (TITLE_TRUNCATION_LIMIT - 10, SUMMARY_TRUNCATION_LIMIT - 10, False),
        ],
    )
    @patch("apps.owasp.api.search.issue.get_issues")
    def test_handler_text_truncation(
        self,
        mock_get_issues,
        title_length,
        summary_length,
        should_truncate,
        mock_slack_client,
        mock_slack_command,
    ):
        long_title = "A" * title_length
        long_summary = "B" * summary_length

        mock_issue = {
            "idx_project_name": "Test Project",
            "idx_summary": long_summary,
            "idx_title": long_title,
            "idx_url": "http://example.com/issue/1",
        }
        mock_get_issues.return_value = {"hits": [mock_issue]}
        settings.SLACK_COMMANDS_ENABLED = True

        handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        truncated_title = Truncator(long_title).chars(TITLE_TRUNCATION_LIMIT, truncate="...")
        truncated_summary = Truncator(long_summary).chars(SUMMARY_TRUNCATION_LIMIT, truncate="...")

        if should_truncate:
            assert any(truncated_title in str(block) for block in blocks)
            assert any(truncated_summary in str(block) for block in blocks)
            assert not any(long_title in str(block) for block in blocks)
            assert not any(long_summary in str(block) for block in blocks)
        else:
            assert any(long_title in str(block) for block in blocks)
            assert any(long_summary in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("search_text", "expected_search", "expected_escaped", "distinct_value"),
        [
            ("", "", "", True),
            ("test<>&", "test<>&", "test&lt;&gt;&amp;", False),
            ("normal search", "normal search", "normal search", False),
        ],
    )
    @patch("apps.owasp.api.search.issue.get_issues")
    def test_handler_search_queries(
        self,
        mock_get_issues,
        search_text,
        expected_search,
        expected_escaped,
        distinct_value,
        mock_slack_client,
    ):
        command = {"text": search_text, "user_id": "U123456"}
        mock_get_issues.return_value = {"hits": []}
        settings.SLACK_COMMANDS_ENABLED = True

        handler(ack=MagicMock(), command=command, client=mock_slack_client)

        mock_get_issues.assert_called_with(
            expected_search,
            attributes=["idx_project_name", "idx_summary", "idx_title", "idx_url"],
            distinct=distinct_value,
            limit=10,
        )

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert any(expected_escaped in str(block) for block in blocks)

    @pytest.mark.parametrize("command_text", sorted(COMMAND_START))
    @patch("apps.owasp.api.search.issue.get_issues")
    def test_handler_start_commands(
        self,
        mock_get_issues,
        command_text,
        mock_slack_client,
    ):
        command = {"text": command_text, "user_id": "U123456"}
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_issues.return_value = {"hits": []}

        handler(ack=MagicMock(), command=command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) > 0
        assert FEEDBACK_CHANNEL_MESSAGE.strip() in str(blocks)
