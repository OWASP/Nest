"""Tests for the ai_create_event_chunks Django management command."""

from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_update_event_chunks import Command
from apps.owasp.models.event import Event


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_event():
    """Return a mock Event instance."""
    event = Mock()
    event.id = 1
    event.key = "test-event"
    return event


class TestAiCreateEventChunksCommand:
    """Test suite for the ai_create_event_chunks command."""

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_model_class_property(self, command):
        """Test the model_class property returns Event."""
        assert command.model_class == Event

    def test_entity_name_property(self, command):
        """Test the entity_name property."""
        assert command.entity_name == "event"

    def test_entity_name_plural_property(self, command):
        """Test the entity_name_plural property."""
        assert command.entity_name_plural == "events"

    def test_key_field_name_property(self, command):
        """Test the key_field_name property."""
        assert command.key_field_name == "key"

    def test_extract_content(self, command, mock_event):
        """Test content extraction from event."""
        with patch(
            "apps.ai.management.commands.ai_update_event_chunks.extract_event_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_event)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_event)

    def test_get_base_queryset(self, command):
        """Test get_base_queryset calls super().get_base_queryset()."""
        with patch(
            "apps.ai.common.base.ai_command.BaseAICommand.get_base_queryset",
            return_value="base_qs",
        ) as mock_super:
            result = command.get_base_queryset()
            assert result == "base_qs"
            mock_super.assert_called_once()

    def test_get_default_queryset(self, command):
        """Test that the default queryset returns upcoming events."""
        with patch("apps.owasp.models.event.Event.upcoming_events") as mock_upcoming:
            mock_queryset = Mock()
            mock_upcoming.return_value = mock_queryset
            result = command.get_default_queryset()
            assert result == mock_queryset
            mock_upcoming.assert_called_once()
