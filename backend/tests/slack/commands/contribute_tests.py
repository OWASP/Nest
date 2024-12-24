from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.utils.text import Truncator

from apps.slack.commands.contribute import (
    COMMAND,
    COMMAND_START,
    SUMMARY_TRUNCATION_LIMIT,
    TITLE_TRUNCATION_LIMIT,
    handler,
)
from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE


@pytest.fixture()
def mock_slack_command():
    return {
        "text": "python",
        "user_id": "U123456",
    }


@pytest.fixture()
def mock_slack_client():
    client = MagicMock()
    client.conversations_open.return_value = {"channel": {"id": "C123456"}}
    return client


@pytest.fixture()
def mock_issue():
    return {
        "idx_project_name": "Test Project",
        "idx_summary": "Test Summary",
        "idx_title": "Test Title",
        "idx_url": "http://example.com/issue/1",
    }


@patch("apps.owasp.api.search.issue.get_issues")
def test_handler_with_no_results(mock_get_issues, mock_slack_client, mock_slack_command):
    mock_get_issues.return_value = {"hits": []}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
    assert any(f"No results found for `{COMMAND}" in str(block) for block in blocks)


@patch("apps.owasp.api.search.issue.get_issues")
def test_handler_with_results(mock_get_issues, mock_slack_client, mock_slack_command, mock_issue):
    mock_get_issues.return_value = {"hits": [mock_issue]}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
    assert any("Here are top 10 most relevant issues" in str(block) for block in blocks)
    assert any(mock_issue["idx_title"] in str(block) for block in blocks)


def test_handler_with_disabled_commands(mock_slack_client, mock_slack_command):
    settings.SLACK_COMMANDS_ENABLED = False

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    mock_slack_client.conversations_open.assert_not_called()
    mock_slack_client.chat_postMessage.assert_not_called()


@patch("apps.owasp.api.search.issue.get_issues")
def test_handler_text_truncation(mock_get_issues, mock_slack_client, mock_slack_command):
    long_title = "A" * (TITLE_TRUNCATION_LIMIT + 10)
    long_summary = "B" * (SUMMARY_TRUNCATION_LIMIT + 10)

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

    assert any(truncated_title in str(block) for block in blocks)
    assert any(truncated_summary in str(block) for block in blocks)
    assert not any(long_title in str(block) for block in blocks)
    assert not any(long_summary in str(block) for block in blocks)


@patch("apps.owasp.api.search.issue.get_issues")
def test_handler_empty_search_query(mock_get_issues, mock_slack_client):
    command = {"text": "", "user_id": "U123456"}
    mock_get_issues.return_value = {"hits": []}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=command, client=mock_slack_client)

    mock_get_issues.assert_called_with(
        "",
        attributes=["idx_project_name", "idx_summary", "idx_title", "idx_url"],
        distinct=True,
        limit=10,
    )


@patch("apps.owasp.api.search.issue.get_issues")
def test_handler_special_characters(mock_get_issues, mock_slack_client):
    command = {"text": "test<>&", "user_id": "U123456"}
    mock_get_issues.return_value = {"hits": []}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
    assert any("test&lt;&gt;&amp;" in str(block) for block in blocks)


START_COMMANDS = sorted(COMMAND_START)


@pytest.mark.parametrize("command_text", START_COMMANDS)
def test_handler_all_start_commands(command_text, mock_slack_client):
    command = {"text": command_text, "user_id": "U123456"}
    settings.SLACK_COMMANDS_ENABLED = True

    with patch("apps.owasp.api.search.issue.get_issues", return_value={"hits": []}):
        handler(ack=MagicMock(), command=command, client=mock_slack_client)

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert len(blocks) > 0
        assert FEEDBACK_CHANNEL_MESSAGE in str(blocks)
