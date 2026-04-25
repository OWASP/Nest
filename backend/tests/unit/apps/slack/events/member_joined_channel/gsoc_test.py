from unittest.mock import MagicMock

import pytest
from django.conf import settings

from apps.slack.constants import OWASP_GSOC_CHANNEL_ID
from apps.slack.events.member_joined_channel.gsoc import Gsoc


class TestGsocEventHandler:
    @pytest.fixture
    def mock_slack_event(self):
        return {"user": "U123456", "channel": OWASP_GSOC_CHANNEL_ID.replace("#", "")}

    @pytest.fixture
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
                    "start your journey",
                    "excited",
                    "feedback",
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

        gsoc = Gsoc()
        gsoc.handler(event=mock_slack_event, client=mock_slack_client, ack=MagicMock())

        if not events_enabled:
            mock_slack_client.chat_postEphemeral.assert_not_called()
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
        else:
            # Check that ephemeral message was sent
            mock_slack_client.chat_postEphemeral.assert_called_once()
            ephemeral_call_args = mock_slack_client.chat_postEphemeral.call_args
            assert ephemeral_call_args[1]["channel"] == mock_slack_event["channel"]
            assert ephemeral_call_args[1]["user"] == mock_slack_event["user"]

            mock_slack_client.conversations_open.assert_called_once_with(
                users=mock_slack_event["user"]
            )

            _, kwargs = mock_slack_client.chat_postMessage.call_args
            blocks = kwargs["blocks"]
            block_texts = []
            for block in blocks:
                if block.get("type") == "section":
                    text = block.get("text", {}).get("text", "")
                    block_texts.append(text)
            combined_text = " ".join(block_texts)

            for message in expected_messages:
                assert message in combined_text

    @pytest.mark.parametrize(
        ("channel_id", "expected_result"),
        [
            (OWASP_GSOC_CHANNEL_ID.replace("#", ""), True),
            ("C999999", False),
        ],
    )
    def test_matcher(self, channel_id, expected_result):
        gsoc = Gsoc()
        assert gsoc.matchers[0]({"channel": channel_id}) == expected_result
