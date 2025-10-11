from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_update_project_chunks import Command


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_project():
    project = Mock()
    project.id = 1
    project.key = "test-project"
    return project


class TestAiCreateProjectChunksCommand:
    def test_command_inheritance(self, command):
        assert isinstance(command, BaseCommand)

    def test_model_class_property(self, command):
        from apps.owasp.models.project import Project

        assert command.model_class == Project

    def test_entity_name_property(self, command):
        assert command.entity_name == "project"

    def test_entity_name_plural_property(self, command):
        assert command.entity_name_plural == "projects"

    def test_key_field_name_property(self, command):
        assert command.key_field_name == "key"

    def test_extract_content(self, command, mock_project):
        with patch(
            "apps.ai.management.commands.ai_update_project_chunks.extract_project_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_project)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_project)

    def test_get_base_queryset_calls_super(self, command):
        """Test that get_base_queryset calls the parent method."""
        with patch(
            "apps.ai.common.base.chunk_command.BaseChunkCommand.get_base_queryset"
        ) as mock_super:
            mock_super.return_value = "base_queryset"
            result = command.get_base_queryset()
            assert result == "base_queryset"
            mock_super.assert_called_once()
