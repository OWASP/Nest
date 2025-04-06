"""Test events command handler."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.utils import timezone

from apps.slack.commands.events import COMMAND, events_handler


class MockEvent:
    def __init__(self, name, category, start_date, end_date, url, description):
        self.name = name
        self.category = category
        self.start_date = start_date
        self.end_date = end_date
        self.url = url
        self.description = description


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

test_event = "Test Event"
test_event_no_url = "Test Event No URL"
upcoming_owasp_events = "Upcoming OWASP Events"


class TestEventsHandler:
    """Test events command handler."""

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
    def test_handler_multiple_categories(
        self, mock_get_events, mock_command, mock_client, mock_event, mock_event_no_url
    ):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_event2 = MagicMock()
        mock_event2.name = "Workshop Event"
        mock_event2.start_date = timezone.now().date()
        mock_event2.end_date = timezone.now().date()
        mock_event2.description = "Workshop Description"
        mock_event2.url = "https://example.com/workshop"
        mock_event2.category = "workshop"

        mock_get_events.return_value = [mock_event, mock_event2, mock_event_no_url]

        events_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "Category: Conference" in text
        assert "Category: Workshop" in text
        assert "Category: Other" in text
        assert test_event in text
        assert "Workshop Event" in text
        assert test_event_no_url in text

    @patch("apps.slack.commands.events.get_events_data")
    def test_handler_invalid_start_date(self, mock_get_events, mock_command, mock_client):
        settings.SLACK_COMMANDS_ENABLED = True
        mock_event_invalid = MagicMock()
        mock_event_invalid.name = "Invalid Event"
        mock_event_invalid.start_date = None
        mock_event_invalid.end_date = None
        mock_event_invalid.description = "This event shouldn't appear"
        mock_event_invalid.url = None
        mock_event_invalid.category = None

        valid_event = MagicMock()
        valid_event.name = "Valid Event"
        valid_event.start_date = timezone.now().date()
        valid_event.end_date = None
        valid_event.description = "This event should appear"
        valid_event.url = None
        valid_event.category = None

        mock_get_events.return_value = [mock_event_invalid, valid_event]

        events_handler(ack=MagicMock(), command=mock_command, client=mock_client)

        blocks = mock_client.chat_postMessage.call_args[1]["blocks"]
        text = "".join(str(block) for block in blocks)

        assert "Valid Event" in text
        assert "This event should appear" in text
        assert "Invalid Event" not in text
        assert "This event shouldn't appear" not in text

    @patch("apps.slack.apps.SlackConfig.app")
    def test_command_registration(self, mock_app):
        import importlib

        from apps.slack.commands import events

        mock_command_decorator = MagicMock()
        mock_app.command.return_value = mock_command_decorator

        importlib.reload(events)

        mock_app.command.assert_called_once_with(COMMAND)
        assert mock_command_decorator.call_count == 1
        assert mock_command_decorator.call_args[0][0].__name__ == "events_handler"
