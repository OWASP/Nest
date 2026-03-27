"""Tests for the ai_create_committee_chunks command."""

from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.management.commands.ai_update_committee_chunks import Command
from apps.owasp.models.committee import Committee


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
    committee.name = "Test Committee"
    committee.description = "Test committee description"
    committee.is_active = True
    return committee


class TestAiCreateCommitteeChunksCommand:
    """Test suite for the ai_create_committee_chunks command."""

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_model_class_method(self, command):
        """Test the model_class method returns Committee."""
        assert command.model_class == Committee

    def test_entity_name_method(self, command):
        """Test the entity_name method."""
        assert command.entity_name == "committee"

    def test_entity_name_plural_method(self, command):
        """Test the entity_name_plural method."""
        assert command.entity_name_plural == "committees"

    def test_key_field_name_method(self, command):
        """Test the key_field_name method."""
        assert command.key_field_name == "key"

    def test_extract_content_method(self, command, mock_committee):
        """Test the extract_content method."""
        with patch(
            "apps.ai.management.commands.ai_update_committee_chunks.extract_committee_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_committee)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_committee)

    def test_get_base_queryset_calls_super(self, command):
        """Test that get_base_queryset calls the parent method."""
        with patch(
            "apps.ai.common.base.chunk_command.BaseChunkCommand.get_base_queryset"
        ) as mock_super:
            mock_super.return_value = "base_queryset"
            result = command.get_base_queryset()
            assert result == "base_queryset"
            mock_super.assert_called_once()

    def test_get_default_queryset_filters_active(self, command):
        """Test that get_default_queryset filters for active committees."""
        with patch.object(command, "get_base_queryset") as mock_get_base:
            mock_queryset = Mock()
            mock_get_base.return_value = mock_queryset
            mock_queryset.filter.return_value = "filtered_queryset"

            result = command.get_default_queryset()

            assert result == "filtered_queryset"
            mock_queryset.filter.assert_called_once_with(is_active=True)

    def test_add_arguments_calls_super(self, command):
        """Test that add_arguments calls the parent method."""
        mock_parser = Mock()
        with patch.object(command, "add_common_arguments") as mock_add_common:
            command.add_arguments(mock_parser)
            mock_add_common.assert_called_once_with(mock_parser)

    def test_get_queryset_with_committee_key(self, command):
        """Test get_queryset with committee key option."""
        with patch.object(command, "get_base_queryset") as mock_get_base:
            mock_queryset = Mock()
            mock_get_base.return_value = mock_queryset
            mock_queryset.filter.return_value = "filtered_queryset"

            options = {"committee_key": "specific-committee"}
            result = command.get_queryset(options)

            assert result == "filtered_queryset"
            mock_queryset.filter.assert_called_once_with(key="specific-committee")

    def test_get_queryset_with_all_option(self, command):
        """Test get_queryset with all option."""
        with patch.object(command, "get_base_queryset") as mock_get_base:
            mock_queryset = Mock()
            mock_get_base.return_value = mock_queryset

            options = {"all": True}
            result = command.get_queryset(options)

            assert result == mock_queryset

    def test_get_queryset_default_behavior(self, command):
        """Test get_queryset with default behavior."""
        with patch.object(command, "get_default_queryset") as mock_get_default:
            mock_get_default.return_value = "default_queryset"

            options = {}
            result = command.get_queryset(options)

            assert result == "default_queryset"

    def test_get_entity_key_returns_key(self, command, mock_committee):
        """Test get_entity_key returns the committee key."""
        result = command.get_entity_key(mock_committee)
        assert result == "test-committee"

    def test_get_entity_key_fallback_to_pk(self, command):
        """Test get_entity_key falls back to pk when key field doesn't exist."""
        mock_committee = Mock()
        mock_committee.pk = 123

        if hasattr(mock_committee, "key"):
            delattr(mock_committee, "key")

        result = command.get_entity_key(mock_committee)
        assert result == "123"

    def test_source_name_default(self, command):
        """Test default source name."""
        assert command.source_name() == "owasp_committee"

    def test_help_method(self, command):
        """Test the help method."""
        assert command.help() == "Create or update chunks for OWASP committee data"
