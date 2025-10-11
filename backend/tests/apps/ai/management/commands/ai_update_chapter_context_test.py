"""Tests for the ai_create_chapter_context Django management command."""

from unittest.mock import Mock, patch

import pytest

from apps.ai.management.commands.ai_update_chapter_context import Command


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_chapter():
    chapter = Mock()
    chapter.id = 1
    chapter.key = "test-chapter"
    return chapter


class TestAiCreateChapterContextCommand:
    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseContextCommand."""
        from apps.ai.common.base.context_command import BaseContextCommand

        assert isinstance(command, BaseContextCommand)

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help() == "Update context for OWASP chapter data"

    def test_model_class_property(self, command):
        """Test the model_class property returns Chapter."""
        from apps.owasp.models.chapter import Chapter

        assert command.model_class == Chapter

    def test_entity_name_property(self, command):
        """Test the entity_name property."""
        assert command.entity_name == "chapter"

    def test_entity_name_plural_property(self, command):
        """Test the entity_name_plural property."""
        assert command.entity_name_plural == "chapters"

    def test_key_field_name_property(self, command):
        """Test the key_field_name property."""
        assert command.key_field_name == "key"

    def test_extract_content(self, command, mock_chapter):
        """Test the extract_content method."""
        with patch(
            "apps.ai.management.commands.ai_update_chapter_context.extract_chapter_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_chapter)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_chapter)
