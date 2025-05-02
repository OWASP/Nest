from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.slack.commands.events import Events, events_handler

test_event = "OWASP Global AppSec 2023"
test_event_no_url = "OWASP Local Chapter Meeting"
upcoming_owasp_events = "Upcoming OWASP Events"


class MockEvent:
    def __init__(self, name, start_date, end_date, suggested_location, url, description):
        self.name = name
        self.start_date = (
            datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
            if start_date
            else None
        )
        self.end_date = (
            datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).date()
            if end_date
            else None
        )
        self.suggested_location = suggested_location
        self.url = url
        self.description = description


mock_events = sorted(
    [
        MockEvent(
            name="OWASP Snow 2025",
            start_date="2025-03-14",
            end_date="2025-03-14",
            suggested_location="Denver, CO",
            url="https://example.com/snow",
            description="Regional conference",
        ),
        MockEvent(
            name="OWASP Global AppSec EU 2025",
            start_date="2025-05-26",
            end_date="2025-05-30",
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
            "text": "",
            "user_id": "U123456",
        }

    @pytest.fixture
    def mock_slack_client(self):
        client = MagicMock()
        client.conversations_open.return_value = {"channel": {"id": "C123456"}}
        return client

    @pytest.fixture
    def mock_event(self):
        event = MagicMock()
        event.name = test_event
        event.start_date = timezone.now().date()
        event.end_date = timezone.now().date()
        event.description = "Test Description"
        event.url = "https://example.com/event"
        event.category = "conference"
        return event

    @pytest.fixture
    def mock_event_no_url(self):
        event = MagicMock()
        event.name = test_event_no_url
        event.start_date = timezone.now().date()
        event.end_date = None
        event.description = "Test Description No URL"
        event.url = None
        event.category = None
        return event

    def test_handler_disabled(self, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = False

        events_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_not_called()
        mock_client.chat_postMessage.assert_not_called()

    @patch("apps.slack.commands.events.get_events_data")
    def test_handler_no_events(self, mock_get_events, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_events.return_value = []

        events_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert upcoming_owasp_events in text
        assert "For more information" in text

    @patch("apps.slack.commands.events.get_events_data")
    def test_handler_none_events_data(self, mock_get_events, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_events.return_value = None

        with (
            patch("apps.slack.commands.events.events_handler", side_effect=events_handler),
            patch("builtins.list", lambda x: [] if x is None else list(x)),
        ):
            events_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        mock_client.conversations_open.assert_called_once_with(users=mock_command["user_id"])
        mock_client.chat_postMessage.assert_called_once()

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert upcoming_owasp_events in text
        assert "For more information" in text

    @patch("apps.slack.commands.events.get_events_data")
    def test_handler_with_events(self, mock_get_events, mock_command, mock_client, mock_event):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_events.return_value = [mock_event]

        events_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert upcoming_owasp_events in text
        assert "Category: Conference" in text
        assert test_event in text
        assert "Test Description" in text
        assert "Start Date" in text
        assert "End Date" in text

    @patch("apps.slack.commands.events.get_events_data")
    def test_handler_event_no_url_no_end_date(
        self, mock_get_events, mock_command, mock_client, mock_event_no_url
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_get_events.return_value = [mock_event_no_url]

        events_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert upcoming_owasp_events in text
        assert "Category: Other" in text
        assert test_event_no_url in text
        assert "Test Description No URL" in text
        assert "End Date" not in text

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
        self._setup_test_environment(mock_get_events_data, commands_enabled, has_events_data)

        ack = MagicMock()
        Events().handler(ack=ack, command=mock_slack_command, client=mock_slack_client)

        ack.assert_called_once()

        if not commands_enabled:
            self._verify_disabled_state(mock_slack_client)
            return

        self._verify_client_calls(mock_slack_client, mock_slack_command)

        sent_blocks = mock_slack_client.chat_postMessage.call_args[1]["blocks"]
        self._verify_header_blocks(sent_blocks, expected_header)

        if has_events_data:
            self._verify_event_blocks(sent_blocks)

    def _setup_test_environment(self, mock_get_events_data, commands_enabled, has_events_data):
        settings.SLACK_COMMANDS_ENABLED = commands_enabled
        mock_get_events_data.return_value = mock_events if has_events_data else []

    def _verify_disabled_state(self, mock_slack_client):
        mock_slack_client.conversations_open.assert_not_called()
        mock_slack_client.chat_postMessage.assert_not_called()

    def _verify_client_calls(self, mock_slack_client, mock_slack_command):
        mock_slack_client.conversations_open.assert_called_once_with(
            users=mock_slack_command["user_id"]
        )
        mock_slack_client.chat_postMessage.assert_called_once()

    def _verify_header_blocks(self, blocks, expected_header):
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["text"] == expected_header
        assert blocks[1]["type"] == "divider"

    def _verify_event_blocks(self, blocks):
        self._verify_event_block(
            blocks,
            mock_events[0],
            "*1. <https://example.com/snow|OWASP Snow 2025>*",
            "Mar 14, 2025",
            "Denver, CO",
        )

        self._verify_event_block(
            blocks,
            mock_events[1],
            "*2. <https://example.com/eu|OWASP Global AppSec EU 2025>*",
            "May 26 — 30, 2025",
            "Amsterdam, Netherlands",
        )

        self._verify_footer_block(blocks)

    def _verify_event_block(self, blocks, event, title_text, date_text, location):
        event_text_found = False
        for block in blocks:
            if block.get("type") == "section" and "text" in block and "text" in block["text"]:
                block_text = block["text"]["text"]
                if (
                    title_text in block_text
                    and date_text in block_text
                    and location in block_text
                    and event.description in block_text
                ):
                    event_text_found = True
                    break
        assert event_text_found, f"Block containing {title_text} details not found or incorrect"

    def _verify_footer_block(self, blocks):
        footer_block = blocks[-1]
        assert footer_block["type"] == "section"
        assert "🔍 For more information about upcoming events" in footer_block["text"]["text"]
