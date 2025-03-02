"""Test events command handler."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.events import events_handler


# Define a mock event class to simulate the new event object structure
class MockEvent:
    def __init__(self, name, category, start_date, end_date, url, description):
        self.name = name
        self.category = category
        self.start_date = start_date
        self.end_date = end_date
        self.url = url
        self.description = description


# Mock event data as objects
mock_events = [
    MockEvent(
        name="OWASP Snow 2025",
        category="AppSec Days",
        start_date="2025-03-14",
        end_date="March 14, 2025",
        url="https://example.com/snow",
        description="Regional conference",
    ),
    MockEvent(
        name="OWASP Global AppSec EU 2025",
        category="Global",
        start_date="2025-05-26",
        end_date="May 26-30, 2025",
        url="https://example.com/eu",
        description="Premier conference",
    ),
]


class TestEventsHandler:
    """Test events command handler."""

    @pytest.fixture()
    def mock_slack_command(self):
        return {
            "user_id": "U123456",
        }

    @pytest.fixture()
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
        """Test handler responses."""
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_events_data.return_value = mock_events if has_events_data else []

        events_handler(ack=MagicMock(), command=mock_slack_command, client=mock_slack_client)

        if not commands_enabled:
            mock_slack_client.conversations_open.assert_not_called()
            mock_slack_client.chat_postMessage.assert_not_called()
            return

        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )

        blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]

        assert blocks[0]["text"]["text"] == expected_header
        assert blocks[1]["type"] == "divider"

        if has_events_data:
            current_block = 2

            assert "*Category: Appsec Days*" in blocks[current_block]["text"]["text"]
            current_block += 1

            event_block = blocks[current_block]["text"]["text"]
            assert "*1. <https://example.com/snow|OWASP Snow 2025>*" in event_block
            assert "Start Date: 2025-03-14" in event_block
            assert "End Date: March 14, 2025" in event_block
            assert "_Regional conference_" in event_block
            current_block += 1

            assert blocks[current_block]["type"] == "divider"
            current_block += 1

            assert "*Category: Global*" in blocks[current_block]["text"]["text"]
            current_block += 1

            event_block = blocks[current_block]["text"]["text"]
            assert "*1. <https://example.com/eu|OWASP Global AppSec EU 2025>*" in event_block
            assert "Start Date: 2025-05-26" in event_block
            assert "End Date: May 26-30, 2025" in event_block
            assert "_Premier conference_" in event_block
            current_block += 1

            footer_block = blocks[-1]["text"]["text"]
            assert "🔍 For more information about upcoming events" in footer_block
