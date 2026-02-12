"""Tests for the ai_create_committee_context command."""

from unittest.mock import Mock, patch

import pytest

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.management.commands.ai_update_committee_context import Command
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


class TestAiCreateCommitteeContextCommand:
    """Test suite for the ai_create_committee_context command."""

    def test_command_inheritance(self, command):
        """Test that the command inherits from BaseContextCommand."""
        assert isinstance(command, BaseContextCommand)

    def test_command_help_text(self, command):
        """Test that the command has the correct help text."""
        assert command.help() == "Update context for OWASP committee data"

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
            "apps.ai.management.commands.ai_update_committee_context.extract_committee_content"
        ) as mock_extract:
            mock_extract.return_value = ("prose content", "metadata content")
            content = command.extract_content(mock_committee)
            assert content == ("prose content", "metadata content")
            mock_extract.assert_called_once_with(mock_committee)

    def test_get_base_queryset_calls_super(self, command):
        """Test that get_base_queryset calls the parent method."""
        with patch(
            "apps.ai.common.base.context_command.BaseContextCommand.get_base_queryset"
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

    def test_process_context_batch_success(self, command, mock_committee):
        """Test successful context batch processing."""
        with patch("apps.ai.common.base.context_command.Context") as mock_context_class:
            mock_context_class.update_data.return_value = True

            with patch.object(command, "extract_content") as mock_extract:
                mock_extract.return_value = ("Content", "Metadata")

                with patch.object(command, "get_entity_key") as mock_get_key:
                    mock_get_key.return_value = "test-committee"

                    with patch.object(command.stdout, "write") as mock_write:
                        result = command.process_context_batch([mock_committee])

                        assert result == 1
                        mock_context_class.update_data.assert_called_once_with(
                            content="Metadata\n\nContent",
                            entity=mock_committee,
                            source="owasp_committee",
                        )
                        mock_write.assert_called_once_with(
                            "Created/updated context for test-committee"
                        )

    def test_process_context_batch_empty_content(self, command, mock_committee):
        """Test context batch processing with empty content."""
        with patch.object(command, "extract_content") as mock_extract:
            mock_extract.return_value = ("", "")

            with patch.object(command, "get_entity_key") as mock_get_key:
                mock_get_key.return_value = "test-committee"

                with patch.object(command.stdout, "write") as mock_write:
                    result = command.process_context_batch([mock_committee])

                    assert result == 0
                    mock_write.assert_called_once_with("No content for committee test-committee")

    def test_process_context_batch_create_failure(self, command, mock_committee):
        """Test context batch processing when Context.update_data fails."""
        with patch("apps.ai.common.base.context_command.Context") as mock_context_class:
            mock_context_class.update_data.return_value = False

            with patch.object(command, "extract_content") as mock_extract:
                mock_extract.return_value = ("Content", "Metadata")

                with patch.object(command, "get_entity_key") as mock_get_key:
                    mock_get_key.return_value = "test-committee"

                    with (
                        patch.object(command.stdout, "write") as mock_write,
                        patch.object(command.style, "ERROR") as mock_error,
                    ):
                        mock_error.return_value = "ERROR: Failed"

                        result = command.process_context_batch([mock_committee])

                        assert result == 0
                        mock_error.assert_called_once_with(
                            "Failed to create/update context for test-committee"
                        )
                        mock_write.assert_called_once_with("ERROR: Failed")

    def test_handle_calls_batch_processing(self, command):
        """Test that handle method calls batch processing."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 2

        with patch.object(command, "get_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = mock_queryset

            with patch.object(command, "handle_batch_processing") as mock_batch_processing:
                options = {"batch_size": 50}
                command.handle(**options)

                mock_get_queryset.assert_called_once_with(options)
                mock_batch_processing.assert_called_once_with(
                    queryset=mock_queryset,
                    batch_size=50,
                    process_batch_func=command.process_context_batch,
                )
