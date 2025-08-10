"""A command to update context for OWASP committee data."""

from unittest.mock import Mock, patch

import pytest

from apps.ai.management.commands.ai_create_committee_context import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_committee():
    """Return a mock Committee instance."""
    committee = Mock()
    committee.id = 1
    committee.key = "test-committee"
    return committee


class TestAiCreateCommitteeContextCommand:
    """Test suite for the ai_create_committee_context command."""

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help == "Update context for OWASP committee data"

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseContextCommand."""
        from apps.ai.common.base import BaseContextCommand

        assert isinstance(command, BaseContextCommand)

    def test_model_class_property(self, command):
        """Test the model_class property returns Committee."""
        from apps.owasp.models.committee import Committee

        assert command.model_class == Committee

    def test_entity_name_property(self, command):
        """Test the entity_name property."""
        assert command.entity_name == "committee"

    def test_entity_name_plural_property(self, command):
        """Test the entity_name_plural property."""
        assert command.entity_name_plural == "committees"

    def test_key_field_name_property(self, command):
        """Test the key_field_name property."""
        assert command.key_field_name == "key"

    def test_extract_content(self, command, mock_committee):
        """Test content extraction from committee."""
        with patch(
            "apps.ai.management.commands.ai_create_committee_context.extract_committee_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_committee)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_committee)
