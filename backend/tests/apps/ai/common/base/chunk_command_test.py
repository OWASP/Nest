"""Tests for the BaseChunkCommand class."""

from datetime import UTC, datetime
from typing import Any
from unittest.mock import Mock, call, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.base.chunk_command import BaseChunkCommand
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context


class ConcreteChunkCommand(BaseChunkCommand):
    """Concrete implementation of BaseChunkCommand for testing."""

    model_class: type[Any] = Mock  # type: ignore[assignment]
    entity_name = "test_entity"
    entity_name_plural = "test_entities"
    key_field_name = "test_key"

    def extract_content(self, entity):
        """Extract content from entity."""
        return ("prose content", "metadata content")


@pytest.fixture
def command():
    """Return a concrete chunk command instance for testing."""
    cmd = ConcreteChunkCommand()
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
    context.content_type_id = 1
    context.object_id = 1
    context.chunks.aggregate.return_value = {"latest_created": None}
    context.chunks.all.return_value.delete.return_value = (0, {})
    context.nest_updated_at = Mock()
    return context


@pytest.fixture
def mock_content_type():
    """Return a mock content type."""
    content_type = Mock(spec=ContentType)
    content_type.id = 1
    return content_type


@pytest.fixture
def mock_chunks():
    """Return a list of mock chunk instances."""
    chunks = []
    for i in range(3):
        chunk = Mock(spec=Chunk)
        chunk.id = i + 1
        chunk.text = f"Chunk text {i + 1}"
        chunk.context_id = 1
        chunks.append(chunk)
    return chunks


class TestBaseChunkCommand:
    """Test suite for the BaseChunkCommand class."""

    def test_command_inheritance(self, command):
        """Test that BaseChunkCommand inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_help_method(self, command):
        """Test the help method returns appropriate help text."""
        expected_help = "Create or update chunks for OWASP test_entity data"
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

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    def test_process_chunks_batch_no_context(
        self,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_content_type,
    ):
        """Test process_chunks_batch when no context is found."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = None

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_chunks_batch([mock_entity])

            assert result == 0
            mock_write.assert_called_once()
            warning_call = mock_write.call_args[0][0]
            assert "No context found for test_entity test-key-123" in str(warning_call)

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    def test_process_chunks_batch_empty_content(
        self,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
    ):
        """Test process_chunks_batch when extracted content is empty."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context

        with (
            patch.object(command, "extract_content", return_value=("", "")),
            patch.object(command.stdout, "write") as mock_write,
        ):
            result = command.process_chunks_batch([mock_entity])

            assert result == 0
            expected_calls = [
                call("Context for test-key-123 requires chunk creation/update"),
                call("No content to chunk for test_entity test-key-123"),
            ]
            mock_write.assert_has_calls(expected_calls)

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    def test_process_chunks_batch_no_chunks_created(
        self,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
    ):
        """Test process_chunks_batch when no chunks are created from text."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context
        mock_split_text.return_value = []

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_chunks_batch([mock_entity])

            assert result == 0
            expected_calls = [
                call("Context for test-key-123 requires chunk creation/update"),
                call("No chunks created for test_entity test-key-123"),
            ]
            mock_write.assert_has_calls(expected_calls)
            call_args = mock_write.call_args[0][0]
            assert "No chunks created for test_entity test-key-123" in call_args

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    def test_process_chunks_batch_already_up_to_date(
        self,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
    ):
        """Test process_chunks_batch when chunks are already up to date."""
        mock_get_content_type.return_value = mock_content_type

        mock_context.nest_updated_at = datetime(2024, 1, 1, tzinfo=UTC)
        mock_context.chunks.aggregate.return_value = {
            "latest_created": datetime(2024, 1, 2, tzinfo=UTC)
        }
        mock_context_filter.return_value.first.return_value = mock_context

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_chunks_batch([mock_entity])

            assert result == 0
            calls = [str(call) for call in mock_write.call_args_list]
            assert any("already up to date" in str(call) for call in calls)

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    @patch("apps.ai.common.base.chunk_command.create_chunks_and_embeddings")
    @patch("apps.ai.models.chunk.Chunk.bulk_save")
    def test_process_chunks_batch_success(
        self,
        mock_bulk_save,
        mock_create_chunks,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
        mock_chunks,
    ):
        """Test successful chunk processing."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context
        mock_split_text.return_value = ["chunk1", "chunk2", "chunk3"]
        mock_create_chunks.return_value = mock_chunks
        command.openai_client = Mock()

        with (
            patch("apps.ai.models.chunk.Chunk.objects.filter") as mock_chunk_filter,
            patch.object(command.stdout, "write") as mock_write,
        ):
            mock_qs = Mock()
            mock_qs.values_list.return_value = []
            mock_chunk_filter.return_value = mock_qs
            result = command.process_chunks_batch([mock_entity])

            assert result == 1
            _, kwargs = mock_create_chunks.call_args
            assert set(kwargs["chunk_texts"]) == {"chunk1", "chunk2", "chunk3"}
            assert kwargs["context"] == mock_context
            assert kwargs["openai_client"] == command.openai_client
            assert kwargs["save"] is False
            mock_bulk_save.assert_called_once_with(mock_chunks)
            mock_write.assert_has_calls(
                [
                    call("Context for test-key-123 requires chunk creation/update"),
                    call(command.style.SUCCESS("Created 3 new chunks for test-key-123")),
                ]
            )

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    @patch("apps.ai.common.base.chunk_command.create_chunks_and_embeddings")
    @patch("apps.ai.models.chunk.Chunk.bulk_save")
    def test_process_chunks_batch_multiple_entities(
        self,
        mock_bulk_save,
        mock_create_chunks,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_context,
        mock_content_type,
        mock_chunks,
    ):
        """Test processing multiple entities in a batch."""
        entities = []
        for i in range(3):
            entity = Mock()
            entity.id = i + 1
            entity.test_key = f"test-key-{i + 1}"
            entity.is_active = True
            entities.append(entity)

        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context
        mock_split_text.return_value = ["chunk1", "chunk2"]
        mock_create_chunks.return_value = mock_chunks[:2]
        command.openai_client = Mock()

        with (
            patch("apps.ai.models.chunk.Chunk.objects.filter") as mock_chunk_filter,
            patch.object(command.stdout, "write"),
        ):
            mock_qs = Mock()
            mock_qs.values_list.return_value = []
            mock_chunk_filter.return_value = mock_qs
            result = command.process_chunks_batch(entities)

            assert result == 3
            assert mock_create_chunks.call_count == 3
            mock_bulk_save.assert_called_once()
            bulk_save_args = mock_bulk_save.call_args[0][0]
            assert len(bulk_save_args) == 6

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    @patch("apps.ai.common.base.chunk_command.create_chunks_and_embeddings")
    def test_process_chunks_batch_create_chunks_fails(
        self,
        mock_create_chunks,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
    ):
        """Test process_chunks_batch when create_chunks_and_embeddings fails."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context
        mock_split_text.return_value = ["chunk1", "chunk2"]
        mock_create_chunks.return_value = None
        command.openai_client = Mock()

        result = command.process_chunks_batch([mock_entity])

        assert result == 0
        mock_create_chunks.assert_called_once()

    def test_process_chunks_batch_content_combination(
        self, command, mock_entity, mock_context, mock_content_type
    ):
        """Test that metadata and prose content are properly combined."""
        with (
            patch(
                "apps.ai.common.base.chunk_command.ContentType.objects.get_for_model"
            ) as mock_get_content_type,
            patch(
                "apps.ai.common.base.chunk_command.Context.objects.filter"
            ) as mock_context_filter,
            patch("apps.ai.models.chunk.Chunk.split_text") as mock_split_text,
            patch(
                "apps.ai.common.base.chunk_command.create_chunks_and_embeddings"
            ) as mock_create_chunks,
            patch("apps.ai.models.chunk.Chunk.bulk_save"),
        ):
            mock_get_content_type.return_value = mock_content_type
            mock_context_filter.return_value.first.return_value = mock_context
            mock_split_text.return_value = ["chunk1"]
            mock_create_chunks.return_value = [Mock()]
            command.openai_client = Mock()

            with patch.object(
                command,
                "extract_content",
                return_value=("prose", "metadata"),
            ):
                with patch("apps.ai.models.chunk.Chunk.objects.filter") as mock_chunk_filter:
                    mock_qs = Mock()
                    mock_qs.values_list.return_value = []
                    mock_chunk_filter.return_value = mock_qs
                    command.process_chunks_batch([mock_entity])

                expected_content = "metadata\n\nprose"
                mock_split_text.assert_called_once_with(expected_content)

            mock_split_text.reset_mock()
            with patch.object(command, "extract_content", return_value=("prose", "")):
                with patch("apps.ai.models.chunk.Chunk.objects.filter") as mock_chunk_filter:
                    mock_qs = Mock()
                    mock_qs.values_list.return_value = []
                    mock_chunk_filter.return_value = mock_qs
                    command.process_chunks_batch([mock_entity])

                mock_split_text.assert_called_with("prose")

    @patch.object(BaseChunkCommand, "setup_openai_client")
    @patch.object(BaseChunkCommand, "get_queryset")
    @patch.object(BaseChunkCommand, "handle_batch_processing")
    def test_handle_method_success(
        self, mock_handle_batch, mock_get_queryset, mock_setup_client, command
    ):
        """Test the handle method with successful setup."""
        mock_setup_client.return_value = True
        mock_queryset = Mock()
        mock_get_queryset.return_value = mock_queryset
        options = {"batch_size": 10}

        command.handle(**options)

        mock_setup_client.assert_called_once()
        mock_get_queryset.assert_called_once_with(options)
        mock_handle_batch.assert_called_once_with(
            queryset=mock_queryset,
            batch_size=10,
            process_batch_func=command.process_chunks_batch,
        )

    @patch.object(BaseChunkCommand, "setup_openai_client")
    def test_handle_method_openai_setup_fails(self, mock_setup_client, command):
        """Test the handle method when OpenAI client setup fails."""
        mock_setup_client.return_value = False
        options = {"batch_size": 10}

        with (
            patch.object(command, "get_queryset") as mock_get_queryset,
            patch.object(command, "handle_batch_processing") as mock_handle_batch,
        ):
            command.handle(**options)

            mock_setup_client.assert_called_once()
            mock_get_queryset.assert_not_called()
            mock_handle_batch.assert_not_called()

    def test_process_chunks_batch_metadata_only_content(
        self, command, mock_entity, mock_context, mock_content_type
    ):
        """Test process_chunks_batch with only metadata content."""
        with (
            patch(
                "apps.ai.common.base.chunk_command.ContentType.objects.get_for_model"
            ) as mock_get_content_type,
            patch(
                "apps.ai.common.base.chunk_command.Context.objects.filter"
            ) as mock_context_filter,
            patch("apps.ai.models.chunk.Chunk.split_text") as mock_split_text,
            patch(
                "apps.ai.common.base.chunk_command.create_chunks_and_embeddings"
            ) as mock_create_chunks,
            patch("apps.ai.models.chunk.Chunk.bulk_save") as mock_bulk_save,
        ):
            mock_get_content_type.return_value = mock_content_type
            mock_context_filter.return_value.first.return_value = mock_context
            mock_split_text.return_value = ["chunk1"]
            mock_create_chunks.return_value = [Mock()]
            command.openai_client = Mock()

            with patch.object(
                command,
                "extract_content",
                return_value=("", "metadata"),
            ):
                with patch("apps.ai.models.chunk.Chunk.objects.filter") as mock_chunk_filter:
                    mock_qs = Mock()
                    mock_qs.values_list.return_value = []
                    mock_chunk_filter.return_value = mock_qs
                    command.process_chunks_batch([mock_entity])

                mock_split_text.assert_called_once_with("metadata\n\n")
                mock_bulk_save.assert_called_once()

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    @patch("apps.ai.common.base.chunk_command.create_chunks_and_embeddings")
    @patch("apps.ai.models.chunk.Chunk.bulk_save")
    def test_process_chunks_batch_with_duplicates(
        self,
        mock_bulk_save,
        mock_create_chunks,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
        mock_chunks,
    ):
        """Test that duplicate chunk texts are filtered out before processing."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context
        mock_split_text.return_value = ["chunk1", "chunk2", "chunk1", "chunk3", "chunk2"]
        mock_create_chunks.return_value = mock_chunks
        command.openai_client = Mock()

        with patch.object(command.stdout, "write"):
            result = command.process_chunks_batch([mock_entity])

            assert result == 1
            mock_split_text.assert_called_once()
            _, kwargs = mock_create_chunks.call_args
            assert set(kwargs["chunk_texts"]) == {"chunk1", "chunk2", "chunk3"}
            assert kwargs["context"] == mock_context
            assert kwargs["openai_client"] == command.openai_client
            assert kwargs["save"] is False
            mock_bulk_save.assert_called_once_with(mock_chunks)

    def test_process_chunks_batch_whitespace_only_content(
        self, command, mock_entity, mock_context, mock_content_type
    ):
        """Test process_chunks_batch with whitespace-only content."""
        with (
            patch(
                "apps.ai.common.base.chunk_command.ContentType.objects.get_for_model"
            ) as mock_get_content_type,
            patch(
                "apps.ai.common.base.chunk_command.Context.objects.filter"
            ) as mock_context_filter,
        ):
            mock_get_content_type.return_value = mock_content_type
            mock_context_filter.return_value.first.return_value = mock_context

            with (
                patch.object(command, "extract_content", return_value=("   \n\t  ", "  \t\n  ")),
                patch.object(command.stdout, "write") as mock_write,
            ):
                result = command.process_chunks_batch([mock_entity])

                assert result == 0
                expected_calls = [
                    call("Context for test-key-123 requires chunk creation/update"),
                    call("No content to chunk for test_entity test-key-123"),
                ]
                mock_write.assert_has_calls(expected_calls)

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    @patch("apps.ai.common.base.chunk_command.create_chunks_and_embeddings")
    @patch("apps.ai.models.chunk.Chunk.bulk_save")
    def test_process_chunks_batch_deletes_stale_chunks(
        self,
        mock_bulk_save,
        mock_create_chunks,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
    ):
        """Test that stale chunks are deleted when context is updated."""
        mock_get_content_type.return_value = mock_content_type

        latest_timestamp = datetime(2024, 1, 1, tzinfo=UTC)
        mock_context.nest_updated_at = datetime(2024, 1, 2, tzinfo=UTC)
        mock_context.chunks.aggregate.return_value = {"latest_created": latest_timestamp}

        mock_delete_qs = Mock()
        mock_delete_qs.delete.return_value = (5, {})
        mock_context.chunks.all.return_value = mock_delete_qs

        mock_context_filter.return_value.first.return_value = mock_context
        mock_split_text.return_value = ["new chunk"]
        mock_create_chunks.return_value = [Mock()]
        command.openai_client = Mock()

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_chunks_batch([mock_entity])

            assert result == 1
            mock_delete_qs.delete.assert_called_once()
            mock_write.assert_any_call("Deleted 5 stale chunks for test-key-123")
            mock_bulk_save.assert_called_once()

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    @patch("apps.ai.common.base.chunk_command.create_chunks_and_embeddings")
    @patch("apps.ai.models.chunk.Chunk.bulk_save")
    @patch("apps.ai.common.base.chunk_command.is_valid_json")
    def test_process_chunks_batch_with_valid_json_content(
        self,
        mock_is_valid_json,
        mock_bulk_save,
        mock_create_chunks,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
    ):
        """Test processing chunks when content is valid JSON."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context

        json_content = '{"key": "value", "data": "test"}'
        mock_is_valid_json.return_value = True
        mock_split_text.return_value = ["chunk1"]
        mock_create_chunks.return_value = [Mock()]
        command.openai_client = Mock()

        with (
            patch.object(command, "extract_content", return_value=(json_content, "metadata")),
            patch.object(command.stdout, "write"),
        ):
            result = command.process_chunks_batch([mock_entity])

            assert result == 1
            mock_split_text.assert_called_once_with(json_content)
            mock_bulk_save.assert_called_once()

    @patch("apps.ai.common.base.chunk_command.ContentType.objects.get_for_model")
    @patch("apps.ai.common.base.chunk_command.Context.objects.filter")
    @patch("apps.ai.models.chunk.Chunk.split_text")
    @patch("apps.ai.common.base.chunk_command.create_chunks_and_embeddings")
    def test_process_chunks_batch_creates_chunks_returns_none(
        self,
        mock_create_chunks,
        mock_split_text,
        mock_context_filter,
        mock_get_content_type,
        command,
        mock_entity,
        mock_context,
        mock_content_type,
    ):
        """Test when create_chunks_and_embeddings returns None or empty list."""
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = mock_context
        mock_split_text.return_value = ["chunk1"]
        mock_create_chunks.return_value = None
        command.openai_client = Mock()

        with patch.object(command.stdout, "write") as mock_write:
            result = command.process_chunks_batch([mock_entity])

            assert result == 0
            success_calls = [
                call
                for call in mock_write.call_args_list
                if "Created" in str(call) and "new chunks" in str(call)
            ]
            assert len(success_calls) == 0
