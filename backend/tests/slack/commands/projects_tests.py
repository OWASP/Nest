from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.projects import COMMAND, handler


@pytest.fixture()
def mock_slack_command():
    return {
        "text": "web application",
        "user_id": "U123456",
    }


@pytest.fixture()
def mock_slack_client():
    client = MagicMock()
    client.conversations_open.return_value = {"channel": {"id": "C123456"}}
    return client


@pytest.fixture()
def mock_project():
    return {
        "idx_name": "Test Project",
        "idx_summary": "Test summary",
        "idx_url": "http://example.com/project/1",
        "idx_contributors_count": 10,
        "idx_forks_count": 5,
        "idx_stars_count": 100,
        "idx_updated_at": "2024-12-01",
        "idx_level": "Level 1",
        "idx_leaders": ["Leader A", "Leader B"],
    }


def test_handler_with_disabled_commands(mock_slack_client, mock_slack_command):
    settings.SLACK_COMMANDS_ENABLED = False

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    mock_slack_client.conversations_open.assert_not_called()
    mock_slack_client.chat_postMessage.assert_not_called()


@patch("apps.owasp.api.search.project.get_projects")
def test_handler_with_no_results(mock_get_projects, mock_slack_client, mock_slack_command):
    mock_get_projects.return_value = {"hits": []}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
    assert any(f"No results found for `{COMMAND}" in str(block) for block in blocks)


@patch("apps.owasp.api.search.project.get_projects")
def test_handler_with_results(
    mock_get_projects, mock_slack_client, mock_slack_command, mock_project
):
    mock_get_projects.return_value = {"hits": [mock_project]}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
    assert any("Here are top 10 most OWASP projects" in str(block) for block in blocks)
    assert any(mock_project["idx_name"] in str(block) for block in blocks)
    assert any(mock_project["idx_url"] in str(block) for block in blocks)
    assert any("Test summary" in str(block) for block in blocks)


@patch("apps.owasp.api.search.project.get_projects")
def test_handler_special_characters(mock_get_projects, mock_slack_client):
    command = {"text": "web app <>&", "user_id": "U123456"}
    mock_get_projects.return_value = {"hits": []}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
    assert any("web app &lt;&gt;&amp;" in str(block) for block in blocks)


@patch("apps.owasp.api.search.project.get_projects")
def test_handler_formatting(
    mock_get_projects, mock_slack_client, mock_slack_command, mock_project
):
    mock_get_projects.return_value = {"hits": [mock_project]}
    settings.SLACK_COMMANDS_ENABLED = True

    handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
    contributors_text = ", 10 contributors"
    forks_text = ", 5 forks"
    stars_text = ", 100 stars"
    leaders_text = "Leader A, Leader B"

    assert any(contributors_text in str(block) for block in blocks)
    assert any(forks_text in str(block) for block in blocks)
    assert any(stars_text in str(block) for block in blocks)
    assert any(leaders_text in str(block) for block in blocks)
    assert any("Test Project" in str(block) for block in blocks)
    assert any("Test summary" in str(block) for block in blocks)
