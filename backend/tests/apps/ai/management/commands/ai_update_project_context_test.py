from unittest.mock import Mock, patch

import pytest

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.management.commands.ai_update_project_context import Command
from apps.owasp.models.project import Project


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_project():
    project = Mock()
    project.id = 1
    project.key = "test-project"
    return project


class TestAiCreateProjectContextCommand:
    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseContextCommand."""
        assert isinstance(command, BaseContextCommand)

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help() == "Update context for OWASP project data"

    def test_model_class_property(self, command):
        """Test the model_class property returns Project."""
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
        """Test the extract_content method."""
        with patch(
            "apps.ai.management.commands.ai_update_project_context.extract_project_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_project)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_project)

    def test_get_base_queryset(self, command):
        """Test the get_base_queryset method."""
        with patch.object(command.__class__.__bases__[0], "get_base_queryset") as mock_super:
            mock_super.return_value = Mock()
            result = command.get_base_queryset()
            mock_super.assert_called_once()
            assert result == mock_super.return_value
