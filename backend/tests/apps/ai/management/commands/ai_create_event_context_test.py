"""Tests for the ai_create_event_context Django management command."""

from unittest.mock import MagicMock, Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_event_context import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_event():
    """Return a mock Event instance."""
    event = Mock()
    event.id = 1
    event.title = "test-event"
    return event


class TestAiCreateEventContextCommand:
    """Test suite for the ai_create_event_context command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Update context for OWASP event data"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_add_arguments(self, command):
        """Test that the command adds the correct arguments."""
        parser = MagicMock()
        command.add_arguments(parser)

        assert parser.add_argument.call_count == 3
        parser.add_argument.assert_any_call(
            "--all",
            action="store_true",
            help="Process all the events",
        )
        parser.add_argument.assert_any_call(
            "--batch-size",
            type=int,
            default=50,
            help="Number of events to process in each batch",
        )

    @patch("apps.ai.management.commands.ai_create_event_context.Event.upcoming_events")
    def test_handle_no_events_found(self, mock_upcoming_events, command):
        """Test command when no events are found."""
        command.stdout = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_upcoming_events.return_value = mock_queryset

        command.handle(event_key=None, all=False, batch_size=50)

    @patch("apps.ai.management.commands.ai_create_event_context.Event.objects")
    def test_handle_with_all_flag(self, mock_event_objects, command, mock_event):
        """Test command with --all flag."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_event])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_event]
        mock_event_objects.all.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(event_key=None, all=True, batch_size=50)

        mock_event_objects.all.assert_called_once()

    @patch("apps.ai.management.commands.ai_create_event_context.Event.upcoming_events")
    def test_handle_default_future_events(self, mock_upcoming_events, command, mock_event):
        """Test command defaults to future events."""
        command.stdout = MagicMock()
        command.style = MagicMock()
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 1
        mock_queryset.__iter__ = lambda _self: iter([mock_event])
        mock_queryset.__getitem__ = lambda _self, _key: [mock_event]
        mock_upcoming_events.return_value = mock_queryset

        with patch.object(command, "process_context_batch", return_value=1):
            command.handle(event_key=None, all=False, batch_size=50)

        # Should filter for future events by default
        mock_upcoming_events.assert_called()
