from unittest.mock import Mock, patch

import pytest

from apps.ai.common.base.chunk_command import BaseChunkCommand
from apps.ai.management.commands.ai_update_repository_chunks import Command
from apps.github.models.repository import Repository


@pytest.fixture
def command():
    return Command()


@pytest.fixture
def mock_repository():
    repository = Mock()
    repository.id = 1
    repository.key = "test-repo"
    repository.is_owasp_site_repository = True
    repository.is_archived = False
    repository.is_empty = False
    return repository


class TestAiUpdateRepositoryChunksCommand:
    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseChunkCommand."""
        assert isinstance(command, BaseChunkCommand)

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help() == "Create or update chunks for OWASP repository data"

    def test_model_class_property(self, command):
        """Test the model_class property returns Repository."""
        assert command.model_class == Repository

    def test_entity_name_property(self, command):
        """Test the entity_name property."""
        assert command.entity_name == "repository"

    def test_entity_name_plural_property(self, command):
        """Test the entity_name_plural property."""
        assert command.entity_name_plural == "repositories"

    def test_key_field_name_property(self, command):
        """Test the key_field_name property."""
        assert command.key_field_name == "key"

    def test_source_name(self, command):
        """Test the source_name method returns the correct value."""
        assert command.source_name() == "owasp_repository"

    def test_extract_content(self, command, mock_repository):
        """Test the extract_content method."""
        with patch(
            "apps.ai.management.commands.ai_update_repository_chunks.extract_repository_content"
        ) as mock_extract:
            mock_extract.return_value = ("json content", "metadata content")
            content = command.extract_content(mock_repository)
            assert content == ("json content", "metadata content")
            mock_extract.assert_called_once_with(mock_repository)

    def test_get_base_queryset(self, command):
        """Test the get_base_queryset method applies correct filters."""
        with patch.object(command.__class__.__bases__[0], "get_base_queryset") as mock_super:
            mock_queryset = Mock()
            mock_super.return_value = mock_queryset
            mock_queryset.filter.return_value = "filtered_queryset"

            result = command.get_base_queryset()

            mock_super.assert_called_once()
            mock_queryset.filter.assert_called_once_with(
                is_owasp_site_repository=True,
                is_archived=False,
                is_empty=False,
            )
            assert result == "filtered_queryset"

    def test_get_default_queryset(self, command):
        """Test the get_default_queryset method returns base queryset."""
        with patch.object(command, "get_base_queryset") as mock_base:
            mock_base.return_value = "base_queryset"

            result = command.get_default_queryset()

            mock_base.assert_called_once()
            assert result == "base_queryset"

    def test_get_default_queryset_avoids_is_active_filter(self, command):
        """Test that get_default_queryset doesn't apply is_active filter like the base class."""
        with patch.object(command, "get_base_queryset") as mock_base:
            mock_base.return_value = "base_queryset"

            result = command.get_default_queryset()

            assert result == "base_queryset"
            mock_base.assert_called_once()

    def test_queryset_filtering_logic(self, command):
        """Test that the queryset filtering logic works correctly."""
        with patch.object(command.__class__.__bases__[0], "get_base_queryset") as mock_super:
            mock_queryset = Mock()
            mock_super.return_value = mock_queryset
            mock_queryset.filter.return_value = "filtered_queryset"

            result = command.get_base_queryset()

            mock_queryset.filter.assert_called_once_with(
                is_owasp_site_repository=True,
                is_archived=False,
                is_empty=False,
            )
            assert result == "filtered_queryset"

    def test_command_initialization(self, command):
        """Test that the command initializes correctly."""
        assert command.model_class is not None
        assert command.key_field_name == "key"
        assert command.entity_name == "repository"
        assert command.entity_name_plural == "repositories"
