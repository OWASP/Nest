"""Tests for the BaseAICommand class."""

import os
from unittest.mock import Mock, patch

import pytest
from django.core.management.base import BaseCommand
from django.db.models import Model, QuerySet

from apps.ai.common.base.ai_command import BaseAICommand


class MockTestModel(Model):
    """Test model for BaseAICommand testing."""

    def __str__(self):
        """Return string representation of MockTestModel."""
        return f"MockTestModel(pk={self.pk})"

    class Meta:
        """Meta class for MockTestModel."""

        app_label = "test"


class ConcreteAICommand(BaseAICommand):
    """Concrete implementation of BaseAICommand for testing."""

    def model_class(self):
        return MockTestModel

    def entity_name(self):
        return "test_entity"

    def entity_name_plural(self):
        return "test_entities"

    def key_field_name(self):
        return "test_key"

    def extract_content(self, entity):
        return ("prose content", "metadata content")


@pytest.fixture
def command():
    """Return a concrete command instance for testing."""
    return ConcreteAICommand()


@pytest.fixture
def mock_entity():
    """Return a mock entity instance."""
    entity = Mock(spec=MockTestModel)
    entity.pk = 1
    entity.test_key = "test-key-123"
    entity.is_active = True
    return entity


@pytest.fixture
def mock_queryset():
    """Return a mock queryset."""
    queryset = Mock(spec=QuerySet)
    queryset.count.return_value = 5
    queryset.filter.return_value = queryset
    queryset.__getitem__ = Mock(return_value=[])
    return queryset


class TestBaseAICommand:
    """Test suite for the BaseAICommand class."""

    def test_command_inheritance(self, command):
        """Test that BaseAICommand inherits from BaseCommand."""
        assert isinstance(command, BaseCommand)

    def test_initialization(self, command):
        """Test command initialization."""
        assert command.openai_client is None

    def test_abstract_methods_implemented(self, command):
        """Test that all abstract methods are properly implemented."""
        assert command.model_class() == MockTestModel
        assert command.entity_name() == "test_entity"
        assert command.entity_name_plural() == "test_entities"
        assert command.key_field_name() == "test_key"

        mock_entity = Mock()
        result = command.extract_content(mock_entity)
        assert result == ("prose content", "metadata content")

    def test_source_name_default(self, command):
        """Test default source_name implementation."""
        result = command.source_name()
        assert result == "owasp_test_entity"

    def test_get_base_queryset(self, command):
        """Test get_base_queryset method."""
        with patch.object(MockTestModel, "objects") as mock_objects:
            mock_manager = Mock()
            mock_objects.all.return_value = mock_manager
            mock_objects.return_value = mock_manager

            command.get_base_queryset()
            mock_objects.all.assert_called_once()

    def test_get_default_queryset(self, command):
        """Test get_default_queryset method."""
        with patch.object(command, "get_base_queryset") as mock_base_qs:
            mock_queryset = Mock()
            mock_filtered_qs = Mock()
            mock_queryset.filter.return_value = mock_filtered_qs
            mock_base_qs.return_value = mock_queryset

            result = command.get_default_queryset()

            mock_base_qs.assert_called_once()
            mock_queryset.filter.assert_called_once_with(is_active=True)
            assert result == mock_filtered_qs

    def test_add_common_arguments(self, command):
        """Test add_common_arguments method."""
        parser = Mock()

        command.add_common_arguments(parser)

        assert parser.add_argument.call_count == 3

        calls = parser.add_argument.call_args_list

        assert calls[0][0] == ("--test_entity-key",)
        assert calls[0][1]["type"] is str
        assert "Process only the test_entity with this key" in calls[0][1]["help"]

        assert calls[1][0] == ("--all",)
        assert calls[1][1]["action"] == "store_true"
        assert "Process all the test_entities" in calls[1][1]["help"]

        assert calls[2][0] == ("--batch-size",)
        assert calls[2][1]["type"] is int
        assert calls[2][1]["default"] == 50
        assert "Number of test_entities to process in each batch" in calls[2][1]["help"]

    def test_add_arguments_calls_common(self, command):
        """Test that add_arguments calls add_common_arguments."""
        parser = Mock()

        with patch.object(command, "add_common_arguments") as mock_add_common:
            command.add_arguments(parser)
            mock_add_common.assert_called_once_with(parser)

    def test_get_queryset_with_entity_key(self, command):
        """Test get_queryset with entity key option."""
        options = {"test_entity_key": "test-key-123"}

        with patch.object(command, "get_base_queryset") as mock_base_qs:
            mock_queryset = Mock()
            mock_filtered_qs = Mock()
            mock_queryset.filter.return_value = mock_filtered_qs
            mock_base_qs.return_value = mock_queryset

            result = command.get_queryset(options)

            mock_base_qs.assert_called_once()
            mock_queryset.filter.assert_called_once_with(test_key="test-key-123")
            assert result == mock_filtered_qs

    def test_get_queryset_with_all_option(self, command):
        """Test get_queryset with all option."""
        options = {"all": True}

        with patch.object(command, "get_base_queryset") as mock_base_qs:
            mock_queryset = Mock()
            mock_base_qs.return_value = mock_queryset

            result = command.get_queryset(options)

            mock_base_qs.assert_called_once()
            assert result == mock_queryset

    def test_get_queryset_default(self, command):
        """Test get_queryset with default options."""
        options = {}

        with patch.object(command, "get_default_queryset") as mock_default_qs:
            mock_queryset = Mock()
            mock_default_qs.return_value = mock_queryset

            result = command.get_queryset(options)

            mock_default_qs.assert_called_once()
            assert result == mock_queryset

    def test_get_entity_key_with_key_field(self, command, mock_entity):
        """Test get_entity_key with existing key field."""
        result = command.get_entity_key(mock_entity)
        assert result == "test-key-123"

    def test_get_entity_key_fallback_to_pk(self, command):
        """Test get_entity_key falls back to pk when key field doesn't exist."""
        entity = Mock()
        entity.pk = 42
        if hasattr(entity, "test_key"):
            delattr(entity, "test_key")

        result = command.get_entity_key(entity)
        assert result == "42"

    @patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-api-key"})
    @patch("apps.ai.common.base.ai_command.openai.OpenAI")
    def test_setup_openai_client_success(self, mock_openai_class, command):
        """Test successful OpenAI client setup."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        result = command.setup_openai_client()

        assert result is True
        assert command.openai_client == mock_client
        mock_openai_class.assert_called_once_with(api_key="test-api-key")

    @patch.dict(os.environ, {}, clear=True)
    def test_setup_openai_client_no_api_key(self, command):
        """Test OpenAI client setup without API key."""
        if "DJANGO_OPEN_AI_SECRET_KEY" in os.environ:
            del os.environ["DJANGO_OPEN_AI_SECRET_KEY"]

        with patch.object(command.stdout, "write") as mock_write:
            result = command.setup_openai_client()

            assert result is False
            assert command.openai_client is None
            mock_write.assert_called_once()
            call_args = mock_write.call_args[0][0]
            assert "DJANGO_OPEN_AI_SECRET_KEY environment variable not set" in str(call_args)

    def test_handle_batch_processing_empty_queryset(self, command, mock_queryset):
        """Test handle_batch_processing with empty queryset."""
        mock_queryset.count.return_value = 0
        process_batch_func = Mock()

        with patch.object(command.stdout, "write") as mock_write:
            command.handle_batch_processing(mock_queryset, 10, process_batch_func)

            mock_write.assert_called_once_with("No test_entities found to process")
            process_batch_func.assert_not_called()

    def test_handle_batch_processing_with_data(self, command):
        """Test handle_batch_processing with data."""
        mock_entities = [Mock() for _ in range(15)]

        mock_queryset = Mock()
        mock_queryset.count.return_value = 15

        def mock_getitem(slice_obj):
            start = slice_obj.start or 0
            stop = slice_obj.stop
            return mock_entities[start:stop]

        mock_queryset.__getitem__ = Mock(side_effect=mock_getitem)

        process_batch_func = Mock(side_effect=[5, 5, 5])

        with patch.object(command.stdout, "write") as mock_write:
            command.handle_batch_processing(mock_queryset, 5, process_batch_func)

            assert process_batch_func.call_count == 3

            calls = process_batch_func.call_args_list
            assert len(calls[0][0][0]) == 5
            assert len(calls[1][0][0]) == 5
            assert len(calls[2][0][0]) == 5

            write_calls = mock_write.call_args_list
            assert len(write_calls) == 2
            assert "Found 15 test_entities to process" in str(write_calls[0])
            assert "Completed processing 15/15 test_entities" in str(write_calls[1])

    def test_handle_batch_processing_partial_processing(self, command):
        """Test handle_batch_processing when some items fail to process."""
        mock_entities = [Mock() for _ in range(10)]

        mock_queryset = Mock()
        mock_queryset.count.return_value = 10

        def mock_getitem(slice_obj):
            start = slice_obj.start or 0
            stop = slice_obj.stop
            return mock_entities[start:stop]

        mock_queryset.__getitem__ = Mock(side_effect=mock_getitem)

        process_batch_func = Mock(side_effect=[3, 2])

        with patch.object(command.stdout, "write") as mock_write:
            command.handle_batch_processing(mock_queryset, 5, process_batch_func)

            assert process_batch_func.call_count == 2

            write_calls = mock_write.call_args_list
            assert len(write_calls) == 2
            assert "Found 10 test_entities to process" in str(write_calls[0])
            assert "Completed processing 5/10 test_entities" in str(write_calls[1])


class TestBaseAICommandAbstractMethods:
    """Test that BaseAICommand abstract methods raise errors when not implemented."""

    def test_cannot_instantiate_base_class_directly(self):
        """Test that BaseAICommand cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAICommand()

    def test_abstract_methods_must_be_implemented(self):
        """Test that subclasses must implement all abstract methods."""

        class IncompleteCommand(BaseAICommand):
            """Incomplete implementation missing required methods."""

        with pytest.raises(TypeError):
            IncompleteCommand()
