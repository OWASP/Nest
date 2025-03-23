from unittest.mock import MagicMock

import pytest
from django.conf import settings

from apps.slack.constants import FEEDBACK_CHANNEL_MESSAGE, OWASP_GSOC_CHANNEL_ID
from apps.slack.events.member_joined_channel.gsoc import gsoc_handler


class TestGsocEventHandler:
    @pytest.fixture()
    def mock_slack_event(self):
        return {"user": "U123456", "channel": OWASP_GSOC_CHANNEL_ID}

    @pytest.fixture()
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("events_enabled", "expected_messages"),
        [
            (False, []),
            (
                True,
                [
                    "Hello <@U123456>",
                    "Here's how you can start your journey",
                    "🎉 We're excited to have you on board",
                    FEEDBACK_CHANNEL_MESSAGE.strip(),
                ],
            ),
        ],
    )
    def test_handler_responses(
        self,
        events_enabled,
        expected_messages,
        mock_slack_event,
        mock_slack_client,
    ):
        settings.SLACK_EVENTS_ENABLED = events_enabled

        gsoc_handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

        if not events_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_event["user"]
            )
            blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

            for message in expected_messages:
                assert any(message in str(block) for block in blocks)

    @pytest.mark.parametrize(
        ("channel_id", "expected_result"),
        [
            (OWASP_GSOC_CHANNEL_ID, True),
            ("C999999", False),
        ],
    )
    def test_check_gsoc_handler(self, channel_id, expected_result):
        gsoc_module = __import__(
            "apps.slack.events.member_joined_channel.gsoc",
            fromlist=["gsoc_handler"],
        )
        check_gsoc_handler = getattr(
            gsoc_module,
            "check_gsoc_handler",
            lambda x: x.get("channel") == OWASP_GSOC_CHANNEL_ID,
        )

        assert check_gsoc_handler({"channel": channel_id}) == expected_result
