from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_update_chapter_chunks import Command


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_chapter():
    chapter = Mock()
    chapter.id = 1
    chapter.key = "test-chapter"
    return chapter


class TestAiCreateChapterChunksCommand:
    def test_command_inheritance(self, command):
        assert isinstance(command, BaseCommand)

    def test_model_class_property(self, command):
        from apps.owasp.models.chapter import Chapter

        assert command.model_class == Chapter

    def test_entity_name_property(self, command):
        assert command.entity_name == "chapter"

    def test_entity_name_plural_property(self, command):
        assert command.entity_name_plural == "chapters"

    def test_key_field_name_property(self, command):
        assert command.key_field_name == "key"

    def test_extract_content(self, command, mock_chapter):
        with patch(
            "apps.ai.management.commands.ai_update_chapter_chunks.extract_chapter_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_chapter)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_chapter)
