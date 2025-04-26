from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.events import Events


class MockEvent:
    def __init__(self, name, start_date, end_date, suggested_location, url, description):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.suggested_location = suggested_location
        self.url = url
        self.description = description


mock_events = sorted(
    [
        MockEvent(
            name="OWASP Snow 2025",
            start_date="2025-03-14",
            end_date="March 14, 2025",
            suggested_location="Denver, CO",
            url="https://example.com/snow",
            description="Regional conference",
        ),
        MockEvent(
            name="OWASP Global AppSec EU 2025",
            start_date="2025-05-26",
            end_date="May 26-30, 2025",
            suggested_location="Amsterdam, Netherlands",
            url="https://example.com/eu",
            description="Premier conference",
        ),
    ],
    key=lambda x: x.start_date,
)


class TestEventsHandler:
    @pytest.fixture
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.mark.parametrize(
        ("commands_enabled", "has_events_data", "expected_header"),
        [
            (False, True, None),
            (True, True, "*Upcoming OWASP Events:*"),
            (True, False, "*Upcoming OWASP Events:*"),
        ],
    )
    @patch("apps.slack.commands.events.get_events_data")
    def test_handler_responses(
        self,
        mock_get_events_data,
        commands_enabled,
        has_events_data,
        expected_header,
        mock_slack_client,
        mock_slack_command,
    ):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_events_data.return_value = mock_events if has_events_data else []
        ack = MagicMock()
        Events().handler(ack=ack, command=mock_slack_command, client=mock_slack_client)

        ack.assert_called_once()

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
            return

        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )
        mock_slack_client.chat_postMessage.assert_called_once()

        sent_blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        assert sent_blocks[0]["type"] == "section"
        assert sent_blocks[0]["text"]["text"] == expected_header
        assert sent_blocks[1]["type"] == "divider"

        if has_events_data:
            event1 = mock_events[0]
            event1_text_found = False
            for block in sent_blocks:
                if block.get("type") == "section" and "text" in block and "text" in block["text"]:
                    block_text = block["text"]["text"]
                    if (
                        f"*1. <{event1.url}|{event1.name}>*" in block_text
                        and f"Start Date: {event1.start_date}" in block_text
                        and f"End Date: {event1.end_date}" in block_text
                        and f"Location: {event1.suggested_location}" in block_text
                        and f"_{event1.description}_" in block_text
                    ):
                        event1_text_found = True
                        break
            assert event1_text_found, "Block containing Event 1 details not found or incorrect"

            event2 = mock_events[1]
            event2_text_found = False
            for block in sent_blocks:
                if block.get("type") == "section" and "text" in block and "text" in block["text"]:
                    block_text = block["text"]["text"]
                    if (
                        f"*2. <{event2.url}|{event2.name}>*" in block_text
                        and f"Start Date: {event2.start_date}" in block_text
                        and f"End Date: {event2.end_date}" in block_text
                        and f"Location: {event2.suggested_location}" in block_text
                        and f"_{event2.description}_" in block_text
                    ):
                        event2_text_found = True
                        break
            assert event2_text_found, "Block containing Event 2 details not found or incorrect"
            footer_block = sent_blocks[-1]
            assert footer_block["type"] == "section"
            assert "🔍 For more information about upcoming events" in footer_block["text"]["text"]
