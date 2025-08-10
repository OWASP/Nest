"""Tests for the base AI command classes."""

import os
from unittest.mock import Mock, call, patch

import pytest
from django.core.management.base import BaseCommand
from django.db import models

from apps.ai.common.base import BaseAICommand, BaseChunkCommand, BaseContextCommand


class MockModel(models.Model):
    """Mock model for testing purposes."""

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        """Return string representation of the model."""
        return self.name

    class Meta:
        """Meta class for MockModel."""

        app_label = "test"


class ConcreteBaseAICommand(BaseAICommand):
    """Concrete implementation of BaseAICommand for testing."""

    @property
    def model_class(self) -> type[models.Model]:
        return MockModel

    @property
    def entity_name(self) -> str:
        return "test"

    @property
    def entity_name_plural(self) -> str:
        return "tests"

    @property
    def key_field_name(self) -> str:
        return "key"

    def extract_content(self, entity: models.Model) -> tuple[str, str]:
        return f"Content for {entity.name}", f"Metadata for {entity.name}"


class ConcreteBaseContextCommand(BaseContextCommand):
    """Concrete implementation of BaseContextCommand for testing."""

    @property
    def model_class(self) -> type[models.Model]:
        return MockModel

    @property
    def entity_name(self) -> str:
        return "test"

    @property
    def entity_name_plural(self) -> str:
        return "tests"

    @property
    def key_field_name(self) -> str:
        return "key"

    def extract_content(self, entity: models.Model) -> tuple[str, str]:
        return f"Content for {entity.name}", f"Metadata for {entity.name}"


class ConcreteBaseChunkCommand(BaseChunkCommand):
    """Concrete implementation of BaseChunkCommand for testing."""

    @property
    def model_class(self) -> type[models.Model]:
        return MockModel

    @property
    def entity_name(self) -> str:
        return "test"

    @property
    def entity_name_plural(self) -> str:
        return "tests"

    @property
    def key_field_name(self) -> str:
        return "key"

    def extract_content(self, entity: models.Model) -> tuple[str, str]:
        return f"Content for {entity.name}", f"Metadata for {entity.name}"


@pytest.fixture
def base_ai_command():
    """Return a concrete BaseAICommand instance."""
    return ConcreteBaseAICommand()


@pytest.fixture
def base_context_command():
    """Return a concrete BaseContextCommand instance."""
    return ConcreteBaseContextCommand()


@pytest.fixture
def base_chunk_command():
    """Return a concrete BaseChunkCommand instance."""
    return ConcreteBaseChunkCommand()


@pytest.fixture
def mock_entity():
    """Return a mock entity."""
    entity = Mock(spec=MockModel)
    entity.name = "Test Entity"
    entity.key = "test-key"
    entity.pk = 1
    entity.is_active = True
    return entity


@pytest.fixture
def mock_queryset():
    """Return a mock queryset."""
    queryset = Mock()
    queryset.count.return_value = 3
    queryset.filter.return_value = queryset
    queryset.__getitem__ = Mock(side_effect=lambda _: [Mock(), Mock()])
    return queryset


class TestBaseAICommand:
    """Test suite for BaseAICommand."""

    def test_command_inheritance(self, base_ai_command):
        """Test that the command inherits from BaseCommand."""
        assert isinstance(base_ai_command, BaseCommand)

    def test_initialization(self, base_ai_command):
        """Test command initialization."""
        assert base_ai_command.openai_client is None

    def test_abstract_properties(self, base_ai_command):
        """Test abstract property implementations."""
        assert base_ai_command.model_class == MockModel
        assert base_ai_command.entity_name == "test"
        assert base_ai_command.entity_name_plural == "tests"
        assert base_ai_command.key_field_name == "key"

    def test_source_name_default(self, base_ai_command):
        """Test default source name."""
        assert base_ai_command.source_name == "owasp_test"

    def test_extract_content_implementation(self, base_ai_command, mock_entity):
        """Test extract_content implementation."""
        prose, metadata = base_ai_command.extract_content(mock_entity)
        assert prose == "Content for Test Entity"
        assert metadata == "Metadata for Test Entity"

    @patch.object(ConcreteBaseAICommand, "model_class", MockModel)
    def test_get_base_queryset(self, base_ai_command):
        """Test get_base_queryset method."""
        with patch.object(MockModel, "objects") as mock_objects:
            mock_objects.all.return_value = "base_queryset"
            result = base_ai_command.get_base_queryset()
            assert result == "base_queryset"
            mock_objects.all.assert_called_once()

    @patch.object(ConcreteBaseAICommand, "get_base_queryset")
    def test_get_default_queryset(self, mock_get_base, base_ai_command):
        """Test get_default_queryset method."""
        mock_queryset = Mock()
        mock_get_base.return_value = mock_queryset
        mock_queryset.filter.return_value = "filtered_queryset"

        result = base_ai_command.get_default_queryset()

        assert result == "filtered_queryset"
        mock_queryset.filter.assert_called_once_with(is_active=True)

    def test_add_common_arguments(self, base_ai_command):
        """Test add_common_arguments method."""
        mock_parser = Mock()
        mock_parser.add_argument = Mock()

        base_ai_command.add_common_arguments(mock_parser)

        expected_calls = [
            call("--test-key", type=str, help="Process only the test with this key"),
            call("--all", action="store_true", help="Process all the tests"),
            call(
                "--batch-size",
                type=int,
                default=50,
                help="Number of tests to process in each batch",
            ),
        ]
        mock_parser.add_argument.assert_has_calls(expected_calls)

    def test_add_arguments_calls_common(self, base_ai_command):
        """Test add_arguments calls add_common_arguments."""
        mock_parser = Mock()
        with patch.object(base_ai_command, "add_common_arguments") as mock_add_common:
            base_ai_command.add_arguments(mock_parser)
            mock_add_common.assert_called_once_with(mock_parser)

    @patch.object(ConcreteBaseAICommand, "get_base_queryset")
    def test_get_queryset_with_key_option(self, mock_get_base, base_ai_command):
        """Test get_queryset with entity key option."""
        mock_queryset = Mock()
        mock_get_base.return_value = mock_queryset
        mock_queryset.filter.return_value = "filtered_queryset"

        options = {"test_key": "specific-key"}
        result = base_ai_command.get_queryset(options)

        assert result == "filtered_queryset"
        mock_queryset.filter.assert_called_once_with(key="specific-key")

    @patch.object(ConcreteBaseAICommand, "get_base_queryset")
    def test_get_queryset_with_all_option(self, mock_get_base, base_ai_command):
        """Test get_queryset with all option."""
        mock_queryset = Mock()
        mock_get_base.return_value = mock_queryset

        options = {"all": True}
        result = base_ai_command.get_queryset(options)

        assert result == mock_queryset

    @patch.object(ConcreteBaseAICommand, "get_default_queryset")
    def test_get_queryset_default(self, mock_get_default, base_ai_command):
        """Test get_queryset with default behavior."""
        mock_get_default.return_value = "default_queryset"

        options = {}
        result = base_ai_command.get_queryset(options)

        assert result == "default_queryset"

    def test_get_entity_key(self, base_ai_command, mock_entity):
        """Test get_entity_key method."""
        result = base_ai_command.get_entity_key(mock_entity)
        assert result == "test-key"

    def test_get_entity_key_fallback_to_pk(self, base_ai_command):
        """Test get_entity_key falls back to pk when key field doesn't exist."""
        mock_entity = Mock()
        mock_entity.pk = 123
        delattr(mock_entity, "key") if hasattr(mock_entity, "key") else None

        result = base_ai_command.get_entity_key(mock_entity)
        assert result == "123"

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-api-key"})
    @patch("apps.ai.common.base.openai.OpenAI")
    def test_setup_openai_client_success(self, mock_openai_class, base_ai_command):
        """Test successful OpenAI client setup."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        result = base_ai_command.setup_openai_client()

        assert result is True
        assert base_ai_command.openai_client == mock_client
        mock_openai_class.assert_called_once_with(api_key="test-api-key")

    @patch.dict(os.environ, {}, clear=True)
    def test_setup_openai_client_no_api_key(self, base_ai_command):
        """Test OpenAI client setup without API key."""
        with (
            patch.object(base_ai_command.stdout, "write") as mock_write,
            patch.object(base_ai_command.style, "ERROR") as mock_error,
        ):
            mock_error.return_value = "ERROR: No API key"

            result = base_ai_command.setup_openai_client()

            assert result is False
            assert base_ai_command.openai_client is None
            mock_error.assert_called_once_with(
                "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            )
            mock_write.assert_called_once_with("ERROR: No API key")

    def test_handle_batch_processing_empty_queryset(self, base_ai_command):
        """Test batch processing with empty queryset."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 0

        with patch.object(base_ai_command.stdout, "write") as mock_write:
            base_ai_command.handle_batch_processing(
                queryset=mock_queryset,
                batch_size=10,
                process_batch_func=Mock(),
            )

            mock_write.assert_called_once_with("No tests found to process")

    def test_handle_batch_processing_with_items(self, base_ai_command):
        """Test batch processing with items."""
        mock_queryset = Mock()
        mock_queryset.count.return_value = 5

        # Mock slicing behavior
        batch1 = [Mock(), Mock()]
        batch2 = [Mock(), Mock()]
        batch3 = [Mock()]

        def getitem_side_effect(slice_obj):
            if slice_obj == slice(0, 2):
                return batch1
            if slice_obj == slice(2, 4):
                return batch2
            if slice_obj == slice(4, 6):
                return batch3
            return []

        mock_queryset.__getitem__ = Mock(side_effect=getitem_side_effect)

        mock_process_func = Mock(side_effect=[2, 2, 1])  # Return processed counts

        with (
            patch.object(base_ai_command.stdout, "write") as mock_write,
            patch.object(base_ai_command.style, "SUCCESS") as mock_success,
        ):
            mock_success.return_value = "SUCCESS: Completed"

            base_ai_command.handle_batch_processing(
                queryset=mock_queryset,
                batch_size=2,
                process_batch_func=mock_process_func,
            )

            # Verify process function was called with correct batches
            expected_calls = [call(batch1), call(batch2), call(batch3)]
            mock_process_func.assert_has_calls(expected_calls)

            # Verify output messages
            assert mock_write.call_count == 2
            mock_write.assert_any_call("Found 5 tests to process")
            mock_success.assert_called_once_with("Completed processing 5/5 tests")


class TestBaseContextCommand:
    """Test suite for BaseContextCommand."""

    def test_command_inheritance(self, base_context_command):
        """Test that the command inherits from BaseAICommand."""
        assert isinstance(base_context_command, BaseAICommand)

    def test_help_property(self, base_context_command):
        """Test help property."""
        assert base_context_command.help == "Update context for OWASP test data"

    @patch("apps.ai.common.base.create_context")
    def test_process_context_batch_success(
        self, mock_create_context, base_context_command
    ):
        """Test successful context batch processing."""
        mock_create_context.return_value = True

        entities = [
            Mock(name="Entity 1", key="key1"),
            Mock(name="Entity 2", key="key2"),
        ]

        with patch.object(base_context_command, "extract_content") as mock_extract:
            mock_extract.side_effect = [
                ("Content 1", "Metadata 1"),
                ("Content 2", "Metadata 2"),
            ]

            with patch.object(base_context_command, "get_entity_key") as mock_get_key:
                mock_get_key.side_effect = ["key1", "key2"]

                result = base_context_command.process_context_batch(entities)

                assert result == 2
                assert mock_create_context.call_count == 2

                # Verify create_context was called with correct parameters
                expected_calls = [
                    call(
                        content="Metadata 1\n\nContent 1",
                        content_object=entities[0],
                        source="owasp_test",
                    ),
                    call(
                        content="Metadata 2\n\nContent 2",
                        content_object=entities[1],
                        source="owasp_test",
                    ),
                ]
                mock_create_context.assert_has_calls(expected_calls)

    @patch("apps.ai.common.base.create_context")
    def test_process_context_batch_empty_content(
        self, mock_create_context, base_context_command
    ):
        """Test context batch processing with empty content."""
        entities = [Mock(name="Empty Entity", key="empty-key")]

        with patch.object(base_context_command, "extract_content") as mock_extract:
            mock_extract.return_value = ("", "")

            with patch.object(base_context_command, "get_entity_key") as mock_get_key:
                mock_get_key.return_value = "empty-key"

                with patch.object(base_context_command.stdout, "write") as mock_write:
                    result = base_context_command.process_context_batch(entities)

                    assert result == 0
                    mock_create_context.assert_not_called()
                    mock_write.assert_called_once_with("No content for test empty-key")

    @patch("apps.ai.common.base.create_context")
    def test_process_context_batch_create_failure(
        self, mock_create_context, base_context_command
    ):
        """Test context batch processing when create_context fails."""
        mock_create_context.return_value = False

        entities = [Mock(name="Failing Entity", key="fail-key")]

        with patch.object(base_context_command, "extract_content") as mock_extract:
            mock_extract.return_value = ("Content", "Metadata")

            with patch.object(base_context_command, "get_entity_key") as mock_get_key:
                mock_get_key.return_value = "fail-key"

                with (
                    patch.object(base_context_command.stdout, "write") as mock_write,
                    patch.object(base_context_command.style, "ERROR") as mock_error,
                ):
                    mock_error.return_value = "ERROR: Failed"

                    result = base_context_command.process_context_batch(entities)

                    assert result == 0
                    mock_error.assert_called_once_with(
                        "Failed to create context for fail-key"
                    )
                    mock_write.assert_called_once_with("ERROR: Failed")

    def test_handle_calls_batch_processing(self, base_context_command):
        """Test handle method calls handle_batch_processing."""
        options = {"batch_size": 25}
        mock_queryset = Mock()

        with patch.object(base_context_command, "get_queryset") as mock_get_queryset:
            mock_get_queryset.return_value = mock_queryset

            with patch.object(
                base_context_command, "handle_batch_processing"
            ) as mock_handle_batch:
                base_context_command.handle(**options)

                mock_get_queryset.assert_called_once_with(options)
                mock_handle_batch.assert_called_once_with(
                    queryset=mock_queryset,
                    batch_size=25,
                    process_batch_func=base_context_command.process_context_batch,
                )


class TestBaseChunkCommand:
    """Test suite for BaseChunkCommand."""

    def test_command_inheritance(self, base_chunk_command):
        """Test that the command inherits from BaseAICommand."""
        assert isinstance(base_chunk_command, BaseAICommand)

    def test_help_property(self, base_chunk_command):
        """Test help property."""
        assert base_chunk_command.help == "Create chunks for OWASP test data"

    @patch("apps.ai.common.base.create_chunks_and_embeddings")
    @patch("apps.ai.common.base.Chunk.bulk_save")
    @patch("apps.ai.common.base.Chunk.split_text")
    @patch("apps.ai.common.base.Context.objects.filter")
    @patch("apps.ai.common.base.ContentType.objects.get_for_model")
    def test_process_chunks_batch_success(
        self,
        mock_get_content_type,
        mock_context_filter,
        mock_split_text,
        mock_bulk_save,
        mock_create_chunks,
        base_chunk_command,
    ):
        """Test successful chunks batch processing."""
        # Setup mocks
        mock_content_type = Mock()
        mock_get_content_type.return_value = mock_content_type

        mock_context = Mock()
        mock_context_filter.return_value.first.return_value = mock_context

        mock_split_text.return_value = ["chunk1", "chunk2"]

        mock_chunks = [Mock(), Mock()]
        mock_create_chunks.return_value = mock_chunks

        entities = [Mock(id=1, name="Entity 1", key="key1")]

        with patch.object(base_chunk_command, "extract_content") as mock_extract:
            mock_extract.return_value = ("Content", "Metadata")

            with patch.object(base_chunk_command, "get_entity_key") as mock_get_key:
                mock_get_key.return_value = "key1"

                result = base_chunk_command.process_chunks_batch(entities)

                assert result == 1
                mock_get_content_type.assert_called_once_with(MockModel)
                mock_context_filter.assert_called_once_with(
                    content_type=mock_content_type, object_id=1
                )
                mock_split_text.assert_called_once_with("Metadata\n\nContent")
                mock_create_chunks.assert_called_once_with(
                    chunk_texts=["chunk1", "chunk2"],
                    context=mock_context,
                    openai_client=base_chunk_command.openai_client,
                    save=False,
                )
                mock_bulk_save.assert_called_once_with(mock_chunks)

    @patch("apps.ai.common.base.Context.objects.filter")
    @patch("apps.ai.common.base.ContentType.objects.get_for_model")
    def test_process_chunks_batch_no_context(
        self, mock_get_content_type, mock_context_filter, base_chunk_command
    ):
        """Test chunks batch processing when no context exists."""
        mock_content_type = Mock()
        mock_get_content_type.return_value = mock_content_type
        mock_context_filter.return_value.first.return_value = None

        entities = [Mock(id=1, name="Entity 1", key="key1")]

        with patch.object(base_chunk_command, "get_entity_key") as mock_get_key:
            mock_get_key.return_value = "key1"

            with (
                patch.object(base_chunk_command.stdout, "write") as mock_write,
                patch.object(base_chunk_command.style, "WARNING") as mock_warning,
            ):
                mock_warning.return_value = "WARNING: No context"

                result = base_chunk_command.process_chunks_batch(entities)

                assert result == 0
                mock_warning.assert_called_once_with("No context found for test key1")
                mock_write.assert_called_once_with("WARNING: No context")

    @patch("apps.ai.common.base.Chunk.split_text")
    @patch("apps.ai.common.base.Context.objects.filter")
    @patch("apps.ai.common.base.ContentType.objects.get_for_model")
    def test_process_chunks_batch_empty_content(
        self,
        mock_get_content_type,
        mock_context_filter,
        mock_split_text,
        base_chunk_command,
    ):
        """Test chunks batch processing with empty content."""
        mock_content_type = Mock()
        mock_get_content_type.return_value = mock_content_type

        mock_context = Mock()
        mock_context_filter.return_value.first.return_value = mock_context

        entities = [Mock(id=1, name="Entity 1", key="key1")]

        with patch.object(base_chunk_command, "extract_content") as mock_extract:
            mock_extract.return_value = ("", "")

            with patch.object(base_chunk_command, "get_entity_key") as mock_get_key:
                mock_get_key.return_value = "key1"

                with patch.object(base_chunk_command.stdout, "write") as mock_write:
                    result = base_chunk_command.process_chunks_batch(entities)

                    assert result == 0
                    mock_split_text.assert_not_called()
                    mock_write.assert_called_once_with(
                        "No content to chunk for test key1"
                    )

    @patch("apps.ai.common.base.Chunk.split_text")
    @patch("apps.ai.common.base.Context.objects.filter")
    @patch("apps.ai.common.base.ContentType.objects.get_for_model")
    def test_process_chunks_batch_no_chunks_created(
        self,
        mock_get_content_type,
        mock_context_filter,
        mock_split_text,
        base_chunk_command,
    ):
        """Test chunks batch processing when no chunks are created."""
        mock_content_type = Mock()
        mock_get_content_type.return_value = mock_content_type

        mock_context = Mock()
        mock_context_filter.return_value.first.return_value = mock_context

        mock_split_text.return_value = []  # No chunks created

        entities = [Mock(id=1, name="Entity 1", key="key1")]

        with patch.object(base_chunk_command, "extract_content") as mock_extract:
            mock_extract.return_value = ("Content", "Metadata")

            with patch.object(base_chunk_command, "get_entity_key") as mock_get_key:
                mock_get_key.return_value = "key1"

                with patch.object(base_chunk_command.stdout, "write") as mock_write:
                    result = base_chunk_command.process_chunks_batch(entities)

                    assert result == 0
                    mock_write.assert_called_once_with(
                        "No chunks created for test key1: `Metadata\n\nContent`"
                    )

    def test_handle_calls_setup_and_batch_processing(self, base_chunk_command):
        """Test handle method calls setup_openai_client and handle_batch_processing."""
        options = {"batch_size": 25}
        mock_queryset = Mock()

        with patch.object(base_chunk_command, "setup_openai_client") as mock_setup:
            mock_setup.return_value = True

            with patch.object(base_chunk_command, "get_queryset") as mock_get_queryset:
                mock_get_queryset.return_value = mock_queryset

                with patch.object(
                    base_chunk_command, "handle_batch_processing"
                ) as mock_handle_batch:
                    base_chunk_command.handle(**options)

                    mock_setup.assert_called_once()
                    mock_get_queryset.assert_called_once_with(options)
                    mock_handle_batch.assert_called_once_with(
                        queryset=mock_queryset,
                        batch_size=25,
                        process_batch_func=base_chunk_command.process_chunks_batch,
                    )

    def test_handle_returns_early_if_setup_fails(self, base_chunk_command):
        """Test handle method returns early if OpenAI client setup fails."""
        with patch.object(base_chunk_command, "setup_openai_client") as mock_setup:
            mock_setup.return_value = False

            with patch.object(base_chunk_command, "get_queryset") as mock_get_queryset:
                base_chunk_command.handle()

                mock_setup.assert_called_once()
                mock_get_queryset.assert_not_called()
