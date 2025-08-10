from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_create_project_context import Command


@pytest.fixture
def command():
    """Return a command instance."""
    return Command()


@pytest.fixture
def mock_project():
    """Return a mock Project instance."""
    project = Mock()
    project.id = 1
    project.key = "test-project"
    return project


class TestAiCreateProjectContextCommand:
    """Test suite for the ai_create_project_context command."""

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_model_class_property(self, command):
        """Test the model_class property returns Project."""
        from apps.owasp.models.project import Project

        assert command.model_class == Project

    def test_entity_name_property(self, command):
        """Test the entity_name property."""
        assert command.entity_name == "project"

    def test_entity_name_plural_property(self, command):
        """Test the entity_name_plural property."""
        assert command.entity_name_plural == "projects"

    def test_key_field_name_property(self, command):
        """Test the key_field_name property."""
        assert command.key_field_name == "key"

    def test_extract_content(self, command, mock_project):
        """Test content extraction from project."""
        with patch(
            "apps.ai.management.commands.ai_create_project_context.extract_project_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_project)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_project)
