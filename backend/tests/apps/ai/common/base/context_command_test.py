"""Tests for the BaseContextCommand class."""

from typing import Any
from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand

from apps.ai.common.base.context_command import BaseContextCommand
from apps.ai.models.context import Context


class ConcreteContextCommand(BaseContextCommand):
    """Concrete implementation of BaseContextCommand for testing."""

    model_class: type[Any] = Mock  # type: ignore[assignment]
    entity_name = "test_entity"
    entity_name_plural = "test_entities"
    key_field_name = "test_key"

    def extract_content(self, entity):
        return ("prose content", "metadata content")


@pytest.fixture
def command():
    """Return a concrete context command instance for testing."""
    cmd = ConcreteContextCommand()
    mock_model = Mock()
    mock_model.__name__ = "TestEntity"
    cmd.model_class = mock_model
    cmd.entity_name = "test_entity"
    cmd.entity_name_plural = "test_entities"
    return cmd


@pytest.fixture
def mock_entity():
    """Return a mock entity instance."""
    entity = Mock()
    entity.id = 1
    entity.test_key = "test-key-123"
    entity.is_active = True
    return entity


@pytest.fixture
def mock_context():
    """Return a mock context instance."""
    context = Mock(spec=Context)
    context.id = 1
    context.content = "test content"
    context.content_type_id = 1
    context.object_id = 1
    return context


class TestBaseContextCommand:
    """Test suite for the BaseContextCommand class."""

    def test_command_inheritance(self, command):
        """Test that BaseContextCommand inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_help_method(self, command):
        """Test the help method returns appropriate help text."""
        expected_help = "Update context for OWASP test_entity data"
        assert command.help() == expected_help

    def test_abstract_methods_implemented(self, command):
        """Test that all abstract methods are properly implemented."""
        assert command.model_class.__name__ == "TestEntity"
        assert command.entity_name == "test_entity"
        assert command.entity_name_plural == "test_entities"
        assert command.key_field_name == "test_key"

        mock_entity = Mock()
        result = command.extract_content(mock_entity)
        assert result == ("prose content", "metadata content")

    def test_process_context_batch_empty_content(self, command, mock_entity):
        """Test process_context_batch when extracted content is empty."""
        with (
            patch.object(command, "extract_content", return_value=("", "")),
            patch.object(command.stdout, "write") as mock_write,
        ):
            result = command.process_context_batch([mock_entity])

            assert result == 0
            mock_write.assert_called_once_with("No content for test_entity test-key-123")

    def test_process_context_batch_whitespace_only_content(self, command, mock_entity):
        """Test process_context_batch with whitespace-only content."""
        with (
            patch.object(command, "extract_content", return_value=("   \n\t  ", "  \t\n  ")),
            patch.object(command.stdout, "write") as mock_write,
        ):
            result = command.process_context_batch([mock_entity])

            assert result == 0
            mock_write.assert_called_once_with("No content for test_entity test-key-123")

    @patch("apps.ai.common.base.context_command.Context")
    def test_process_context_batch_success(
        self, mock_context_class, command, mock_entity, mock_context
    ):
        """Test successful context processing."""
        mock_context_class.update_data.return_value = mock_context

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_context_batch([mock_entity])

            assert result == 1
            mock_context_class.update_data.assert_called_once_with(
                content="metadata content\n\nprose content",
                entity=mock_entity,
                source="owasp_test_entity",
            )
            mock_write.assert_called_once_with("Created context for test-key-123")

    @patch("apps.ai.common.base.context_command.Context")
    def test_process_context_batch_creation_fails(self, mock_context_class, command, mock_entity):
        """Test process_context_batch when context creation fails."""
        mock_context_class.update_data.return_value = None

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_context_batch([mock_entity])

            assert result == 0
            mock_context_class.update_data.assert_called_once()
            mock_write.assert_called_once()
            call_args = mock_write.call_args[0][0]
            assert "Failed to create context for test-key-123" in str(call_args)

    @patch("apps.ai.common.base.context_command.Context")
    def test_process_context_batch_multiple_entities(
        self, mock_context_class, command, mock_context
    ):
        """Test processing multiple entities in a batch."""
        entities = []
        for i in range(3):
            entity = Mock()
            entity.id = i + 1
            entity.test_key = f"test-key-{i + 1}"
            entity.is_active = True
            entities.append(entity)

        mock_context_class.update_data.return_value = mock_context

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_context_batch(entities)

            assert result == 3
            assert mock_context_class.update_data.call_count == 3
            assert mock_write.call_count == 3

            calls = mock_context_class.update_data.call_args_list
            for i, call in enumerate(calls):
                _, kwargs = call
                assert kwargs["entity"] == entities[i]
                assert kwargs["content"] == "metadata content\n\nprose content"
                assert kwargs["source"] == "owasp_test_entity"

    @patch("apps.ai.common.base.context_command.Context")
    def test_process_context_batch_mixed_success_failure(
        self, mock_context_class, command, mock_context
    ):
        """Test processing where some entities succeed and others fail."""
        entities = []
        for i in range(3):
            entity = Mock()
            entity.id = i + 1
            entity.test_key = f"test-key-{i + 1}"
            entity.is_active = True
            entities.append(entity)

        mock_context_class.update_data.side_effect = [mock_context, None, mock_context]

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_context_batch(entities)

            assert result == 2
            assert mock_context_class.update_data.call_count == 3
            assert mock_write.call_count == 3

            write_calls = mock_write.call_args_list
            assert "Created context for test-key-1" in str(write_calls[0])
            assert "Failed to create context for test-key-2" in str(write_calls[1])
            assert "Created context for test-key-3" in str(write_calls[2])

    def test_process_context_batch_content_combination(self, command, mock_entity, mock_context):
        """Test that metadata and prose content are properly combined."""
        with patch("apps.ai.common.base.context_command.Context") as mock_context_class:
            mock_context_class.update_data.return_value = mock_context

            with patch.object(command, "extract_content", return_value=("prose", "metadata")):
                command.process_context_batch([mock_entity])

                expected_content = "metadata\n\nprose"
                mock_context_class.update_data.assert_called_once()
                call_args = mock_context_class.update_data.call_args[1]
                assert call_args["content"] == expected_content

            mock_context_class.update_data.reset_mock()
            with patch.object(command, "extract_content", return_value=("prose", "")):
                command.process_context_batch([mock_entity])

                call_args = mock_context_class.update_data.call_args[1]
                assert call_args["content"] == "prose"

    def test_process_context_batch_metadata_only_content(self, command, mock_entity, mock_context):
        """Test process_context_batch with only metadata content."""
        with patch("apps.ai.common.base.context_command.Context") as mock_context_class:
            mock_context_class.update_data.return_value = mock_context

            with patch.object(command, "extract_content", return_value=("", "metadata")):
                command.process_context_batch([mock_entity])

                expected_content = "metadata\n\n"
                call_args = mock_context_class.update_data.call_args[1]
                assert call_args["content"] == expected_content

    @patch.object(BaseContextCommand, "get_queryset")
    @patch.object(BaseContextCommand, "handle_batch_processing")
    def test_handle_method(self, mock_handle_batch, mock_get_queryset, command):
        """Test the handle method."""
        mock_queryset = Mock()
        mock_get_queryset.return_value = mock_queryset
        options = {"batch_size": 10}

        command.handle(**options)

        mock_get_queryset.assert_called_once_with(options)
        mock_handle_batch.assert_called_once_with(
            queryset=mock_queryset,
            batch_size=10,
            process_batch_func=command.process_context_batch,
        )

    def test_source_name_usage(self, command, mock_entity, mock_context):
        """Test that source_name is properly used in context creation."""
        with (
            patch("apps.ai.common.base.context_command.Context") as mock_context_class,
            patch.object(command, "source_name", return_value="custom_source"),
        ):
            mock_context_class.update_data.return_value = mock_context

            command.process_context_batch([mock_entity])

            call_args = mock_context_class.update_data.call_args[1]
            assert call_args["source"] == "custom_source"

    def test_get_entity_key_usage(self, command, mock_context):
        """Test that get_entity_key is properly used for display messages."""
        entity = Mock()
        entity.test_key = "custom-entity-key"

        with patch("apps.ai.common.base.context_command.Context") as mock_context_class:
            mock_context_class.update_data.return_value = mock_context

            with patch.object(command.stdout, "write") as mock_write:
                command.process_context_batch([entity])

                mock_write.assert_called_once_with("Created context for custom-entity-key")

    def test_process_context_batch_empty_list(self, command):
        """Test process_context_batch with empty entity list."""
        result = command.process_context_batch([])
        assert result == 0

    def test_process_context_batch_skips_empty_entities(self, command):
        """Test that entities with empty content are properly skipped."""
        entities = []

        entity1 = Mock()
        entity1.test_key = "entity-1"
        entities.append(entity1)

        entity2 = Mock()
        entity2.test_key = "entity-2"
        entities.append(entity2)

        entity3 = Mock()
        entity3.test_key = "entity-3"
        entities.append(entity3)

        def mock_extract_content(entity):
            if entity.test_key == "entity-2":
                return ("", "")
            return ("prose", "metadata")

        with (
            patch.object(command, "extract_content", side_effect=mock_extract_content),
            patch("apps.ai.common.base.context_command.Context") as mock_context_class,
            patch.object(command.stdout, "write") as mock_write,
        ):
            mock_context_class.update_data.return_value = Mock()

            result = command.process_context_batch(entities)

            assert result == 2
            assert mock_context_class.update_data.call_count == 2

            write_calls = [str(call) for call in mock_write.call_args_list]
            assert any("No content for test_entity entity-2" in call for call in write_calls)
