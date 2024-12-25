from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.constants import (
    FEEDBACK_CHANNEL_MESSAGE,
    NEST_BOT_NAME,
    OWASP_CONTRIBUTE_CHANNEL_ID,
)
from apps.slack.events.user_joined_channel.contribute import contribute_handler


@pytest.fixture()
def mock_slack_event():
    return {"user": "U123456", "channel": OWASP_CONTRIBUTE_CHANNEL_ID}


@pytest.fixture()
def mock_slack_client():
    client = MagicMock()
    client.conversations_open.return_value = {"channel": {"id": "C123456"}}
    return client


def test_contribute_handler_with_events_disabled(mock_slack_event, mock_slack_client):
    settings.SLACK_EVENTS_ENABLED = False

    contribute_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

    mock_slack_client.conversations_open.assert_not_called()
    mock_slack_client.chat_postMessage.assert_not_called()


@patch("apps.owasp.models.project.Project.active_projects_count", return_value=20)
@patch("apps.github.models.issue.Issue.open_issues_count", return_value=50)
def test_contribute_handler_with_event(
    mock_active_projects_count, mock_open_issues_count, mock_slack_event, mock_slack_client
):
    settings.SLACK_EVENTS_ENABLED = True

    contribute_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

    mock_slack_client.conversations_open.assert_called_once_with(users="U123456")

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

    mock_active_projects_count.assert_called_once()
    mock_open_issues_count.assert_called_once()

    assert any("20 active OWASP projects" in str(block) for block in blocks)
    assert any("50 recently opened issues" in str(block) for block in blocks)
    assert any(NEST_BOT_NAME in str(block) for block in blocks)
    assert any("/contribute --start" in str(block) for block in blocks)
    assert any(FEEDBACK_CHANNEL_MESSAGE in str(block) for block in blocks)


def test_check_contribute_handler():
    contribute_module = __import__(
        "apps.slack.events.user_joined_channel.contribute", fromlist=["contribute_handler"]
    )
    check_contribute_handler = getattr(
        contribute_module,
        "check_contribute_handler",
        lambda x: x.get("channel") == OWASP_CONTRIBUTE_CHANNEL_ID,
    )

    assert check_contribute_handler({"channel": OWASP_CONTRIBUTE_CHANNEL_ID})
    assert not check_contribute_handler({"channel": "C999999"})
