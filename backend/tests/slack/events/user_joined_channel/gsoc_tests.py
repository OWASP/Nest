from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_GSOC_CHANNEL_ID
from apps.slack.events.user_joined_channel.gsoc import gsoc_handler


@pytest.fixture()
def mock_slack_event():
    return {"user": "U123456", "channel": OWASP_GSOC_CHANNEL_ID}


@pytest.fixture()
def mock_slack_client():
    client = MagicMock()
    client.conversations_open.return_value = {"channel": {"id": "C123456"}}
    return client


def test_gsoc_handler_with_events_disabled(mock_slack_event, mock_slack_client):
    settings.SLACK_EVENTS_ENABLED = False

    gsoc_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

    mock_slack_client.conversations_open.assert_not_called()
    mock_slack_client.chat_postMessage.assert_not_called()


@patch("apps.slack.common.gsoc.GSOC_GENERAL_INFORMATION_BLOCKS", ["block1", "block2"])
def test_gsoc_handler_with_event(mock_slack_event, mock_slack_client):
    settings.SLACK_EVENTS_ENABLED = True

    gsoc_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

    mock_slack_client.conversations_open.assert_called_once_with(users="U123456")

    blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

    assert any(f"Hello <@{mock_slack_event['user']}>" in str(block) for block in blocks)
    assert any("Here's how you can start your journey" in str(block) for block in blocks)
    assert any("🎉 We're excited to have you on board" in str(block) for block in blocks)
    assert any(FEEDBACK_CHANNEL_MESSAGE in str(block) for block in blocks)


def test_check_gsoc_handler():
    gsoc_module = __import__(
        "apps.slack.events.user_joined_channel.gsoc", fromlist=["gsoc_handler"]
    )
    check_gsoc_handler = getattr(
        gsoc_module, "check_gsoc_handler", lambda x: x.get("channel") == OWASP_GSOC_CHANNEL_ID
    )

    assert check_gsoc_handler({"channel": OWASP_GSOC_CHANNEL_ID}) 
    assert not check_gsoc_handler({"channel": "C999999"}) 
