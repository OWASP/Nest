"""Tests for the ai_create_event_context Django management command."""

from unittest.mock import Mock, patch

import pytest

from apps.ai.management.commands.ai_update_event_context import Command


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_event():
    event = Mock()
    event.id = 1
    event.key = "test-event"
    return event


class TestAiCreateEventContextCommand:
    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseContextCommand."""
        from apps.ai.common.base.context_command import BaseContextCommand

        assert isinstance(command, BaseContextCommand)

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help() == "Update context for OWASP event data"

    def test_model_class_property(self, command):
        """Test the model_class property returns Event."""
        from apps.owasp.models.event import Event

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
        """Test the extract_content method."""
        with patch(
            "apps.ai.management.commands.ai_update_event_context.extract_event_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_event)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_event)

    def test_get_default_queryset(self, command):
        """Test that the default queryset returns upcoming events."""
        with patch("apps.owasp.models.event.Event.upcoming_events") as mock_upcoming:
            mock_queryset = Mock()
            mock_upcoming.return_value = mock_queryset
            result = command.get_default_queryset()
            assert result == mock_queryset
            mock_upcoming.assert_called_once()

    def test_get_base_queryset(self, command):
        """Test the get_base_queryset method."""
        with patch.object(command.__class__.__bases__[0], "get_base_queryset") as mock_super:
            mock_super.return_value = Mock()
            result = command.get_base_queryset()
            mock_super.assert_called_once()
            assert result == mock_super.return_value
