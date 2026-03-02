from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.events import Events, get_events_data


class MockEvent:
    def __init__(self, name, start_date, end_date, location, url, description):
        self.name = name
        self.start_date = (
            datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC).date()
            if start_date
            else None
        )
        self.end_date = (
            datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=UTC).date()
            if end_date
            else None
        )
        self.location = location
        self.suggested_location = location
        self.url = url
        self.description = description


mock_events = sorted(
    [
        MockEvent(
            name="OWASP Snow 2025",
            start_date="2025-03-14",
            end_date="2025-03-14",
            location="Denver, CO",
            url="https://example.com/snow",
            description="Regional conference",
        ),
        MockEvent(
            name="OWASP Global AppSec EU 2025",
            start_date="2025-05-26",
            end_date="2025-05-30",
            location="Amsterdam, Netherlands",
            url="https://example.com/eu",
            description="Premier conference",
        ),
    ],
    key=lambda x: x.start_date or datetime.max.replace(tzinfo=UTC).date(),
)


class TestGetEventsData:
    """Tests for get_events_data function."""

    @patch("apps.owasp.models.event.Event.upcoming_events")
    def test_get_events_data(self, mock_upcoming_events):
        """Test get_events_data returns list of event data."""
        mock_upcoming_events.return_value = mock_events
        result = get_events_data()
        assert isinstance(result, list)
        assert len(result) == len(mock_events)


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
        # Check that the header is in the first block
        assert expected_header in sent_blocks[0]["text"]["text"]

        if has_events_data:
            event1 = mock_events[0]
            event1_text_found = False
            # Check all blocks for event 1
            for block in sent_blocks:
                if block.get("type") == "section" and "text" in block and "text" in block["text"]:
                    block_text = block["text"]["text"]
                    if (
                        f"*<{event1.url}|{event1.name}>*" in block_text
                        and "Mar 14, 2025" in block_text
                        and "Denver, CO" in block_text
                        and event1.description in block_text
                    ):
                        event1_text_found = True
                        break
            assert event1_text_found, "Block containing Event 1 details not found or incorrect"

            event2 = mock_events[1]
            event2_text_found = False
            # Check all blocks for event 2
            for block in sent_blocks:
                if block.get("type") == "section" and "text" in block and "text" in block["text"]:
                    block_text = block["text"]["text"]
                    if (
                        f"*<{event2.url}|{event2.name}>*" in block_text
                        and "May 26 — 30, 2025" in block_text
                        and "Amsterdam, Netherlands" in block_text
                        and event2.description in block_text
                    ):
                        event2_text_found = True
                        break
            assert event2_text_found, "Block containing Event 2 details not found or incorrect"

            # Check that the footer is in one of the blocks
            footer_found = False
            for block in sent_blocks:
                if block.get("type") == "section" and "text" in block and "text" in block["text"]:
                    block_text = block["text"]["text"]
                    if "🔍 For more information about upcoming events" in block_text:
                        footer_found = True
                        break
            assert footer_found, "Footer not found in any block"
