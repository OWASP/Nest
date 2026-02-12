"""Unit tests for AI app context model."""

from unittest.mock import Mock, PropertyMock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from apps.ai.models.context import Context
from apps.common.models import TimestampedModel


def create_model_mock(model_class):
    mock = Mock(spec=model_class)
    mock._state = Mock()
    mock.pk = 1
    mock.id = 1
    mock.chunks = Mock()
    mock.chunks.count.return_value = 0
    return mock


class TestContextModel:
    def test_meta_class_attributes(self):
        assert Context._meta.db_table == "ai_contexts"
        assert Context._meta.verbose_name == "Context"

    def test_content_field_properties(self):
        field = Context._meta.get_field("content")
        assert field.verbose_name == "Generated Text"
        assert field.__class__.__name__ == "TextField"

    def test_content_type_field_properties(self):
        field = Context._meta.get_field("entity_type")
        assert field.null is False
        assert field.blank is False
        assert hasattr(field, "remote_field")
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_object_id_field_properties(self):
        field = Context._meta.get_field("entity_id")
        assert field.__class__.__name__ == "PositiveIntegerField"

    def test_source_field_properties(self):
        field = Context._meta.get_field("source")
        assert field.max_length == 100
        assert field.blank is True
        assert field.default == ""

    @patch("apps.ai.models.context.Context.save")
    @patch("apps.ai.models.context.Context.__init__")
    def test_context_creation_with_save(self, mock_init, mock_save):
        mock_init.return_value = None

        content = "Test generated text"
        source = "test_source"

        context = Context(content=content, source=source)
        context.save()

        mock_save.assert_called_once()

    def test_context_inheritance_from_timestamped_model(self):
        assert issubclass(Context, TimestampedModel)

    @patch("apps.ai.models.context.Context.objects.create")
    def test_context_manager_create(self, mock_create):
        mock_context = create_model_mock(Context)
        mock_create.return_value = mock_context

        content = "Test text"
        source = "test_source"

        result = Context.objects.create(content=content, source=source)

        mock_create.assert_called_once_with(content=content, source=source)
        assert result == mock_context

    @patch("apps.ai.models.context.Context.objects.filter")
    def test_context_manager_filter(self, mock_filter):
        mock_queryset = Mock()
        mock_filter.return_value = mock_queryset

        result = Context.objects.filter(source="test_source")

        mock_filter.assert_called_once_with(source="test_source")
        assert result == mock_queryset

    @patch("apps.ai.models.context.Context.objects.get")
    def test_context_manager_get(self, mock_get):
        mock_context = create_model_mock(Context)
        mock_get.return_value = mock_context

        result = Context.objects.get(id=1)

        mock_get.assert_called_once_with(id=1)
        assert result == mock_context

    @patch("apps.ai.models.context.Context.full_clean")
    def test_context_validation(self, mock_full_clean):
        context = Context()
        context.content = "Valid text"
        context.source = "A" * 100

        context.full_clean()

        mock_full_clean.assert_called_once()

    @patch("apps.ai.models.context.Context.full_clean")
    def test_context_validation_source_too_long(self, mock_full_clean):
        mock_full_clean.side_effect = ValidationError("Source too long")

        context = Context()
        context.content = "Valid text"
        context.source = "A" * 101

        with pytest.raises(ValidationError) as exc_info:
            context.full_clean()
        assert "Source too long" in str(exc_info.value)

    def test_context_default_values(self):
        context = Context()

        assert context.source == ""

    @patch("apps.ai.models.context.Context.refresh_from_db")
    def test_context_refresh_from_db(self, mock_refresh):
        context = Context()
        context.refresh_from_db()

        mock_refresh.assert_called_once()

    @patch("apps.ai.models.context.Context.delete")
    def test_context_delete(self, mock_delete):
        context = Context()
        context.delete()

        mock_delete.assert_called_once()

    @patch("apps.ai.models.context.Context.objects.get")
    def test_update_data_existing_context(self, mock_get):
        mock_context = create_model_mock(Context)
        mock_get.return_value = mock_context

        content = "Test"
        mock_content_object = Mock()
        mock_content_object.pk = 1

        with patch(
            "apps.ai.models.context.ContentType.objects.get_for_model"
        ) as mock_get_for_model:
            mock_content_type = Mock()
            mock_content_type.get_source_expressions = Mock(return_value=[])
            mock_get_for_model.return_value = mock_content_type

            result = Context.update_data(content, mock_content_object, source="src", save=True)

            mock_get_for_model.assert_called_once_with(mock_content_object)
            mock_get.assert_called_once_with(
                entity_type=mock_content_type,
                entity_id=1,
                source="src",
            )
            assert result == mock_context
            assert mock_context.content == content

    def test_str_method_with_name_attribute(self):
        """Test __str__ method when entity has name attribute."""
        content_object = Mock()
        content_object.name = "Test Object"

        entity_type = Mock(spec=ContentType)
        entity_type.model = "test_model"

        context = Context()
        context.content = (
            "This is test content that is longer than 50 characters to test truncation"
        )
        context.entity_type_id = 1
        context.entity_id = "123"

        with (
            patch.object(
                type(context),
                "entity",
                new_callable=PropertyMock,
                return_value=content_object,
            ),
            patch.object(
                type(context),
                "entity_type",
                new_callable=PropertyMock,
                return_value=entity_type,
            ),
        ):
            result = str(context)
            assert (
                result
                == "test_model Test Object: This is test content that is longer than 50 cha..."
            )

    def test_str_method_with_key_attribute(self):
        """Test __str__ method when entity has key but no name attribute."""
        content_object = Mock()
        content_object.name = None
        content_object.key = "test-key"

        entity_type = Mock(spec=ContentType)
        entity_type.model = "test_model"

        context = Context()
        context.content = "Short content"
        context.entity_type_id = 1
        context.entity_id = "123"

        with (
            patch.object(
                type(context),
                "entity",
                new_callable=PropertyMock,
                return_value=content_object,
            ),
            patch.object(
                type(context),
                "entity_type",
                new_callable=PropertyMock,
                return_value=entity_type,
            ),
        ):
            result = str(context)
            assert result == "test_model test-key: Short content"

    def test_str_method_with_neither_name_nor_key(self):
        """Test __str__ method when entity has neither name nor key attribute."""
        content_object = Mock()
        content_object.name = None
        content_object.key = None
        content_object.__str__ = Mock(return_value="Unknown")

        entity_type = Mock(spec=ContentType)
        entity_type.model = "test_model"

        context = Context()
        context.content = "Another test content"
        context.entity_type_id = 1
        context.entity_id = "456"

        with (
            patch.object(
                type(context),
                "entity",
                new_callable=PropertyMock,
                return_value=content_object,
            ),
            patch.object(
                type(context),
                "entity_type",
                new_callable=PropertyMock,
                return_value=entity_type,
            ),
        ):
            result = str(context)
            assert result == "test_model Unknown: Another test content"

    def test_str_method_fallback_to_str(self):
        """Test __str__ method falls back to str(entity)."""
        content_object = Mock()
        content_object.name = None
        content_object.key = None
        content_object.__str__ = Mock(return_value="String representation")

        entity_type = Mock(spec=ContentType)
        entity_type.model = "test_model"

        context = Context()
        context.content = "Test content"
        context.entity_type_id = 1
        context.entity_id = "123"

        with (
            patch.object(
                type(context),
                "entity",
                new_callable=PropertyMock,
                return_value=content_object,
            ),
            patch.object(
                type(context),
                "entity_type",
                new_callable=PropertyMock,
                return_value=entity_type,
            ),
        ):
            result = str(context)
            assert result == "test_model String representation: Test content"

    @patch("apps.ai.models.context.Context.objects.get")
    @patch("apps.ai.models.context.Context.__init__")
    def test_update_data_new_context_with_save(self, mock_init, mock_get):
        """Test update_data creating a new context with save=True."""
        mock_get.side_effect = Context.DoesNotExist
        mock_init.return_value = None  # __init__ should return None

        content = "New test content"
        mock_content_object = Mock()
        mock_content_object.pk = 1
        source = "test_source"

        with patch(
            "apps.ai.models.context.ContentType.objects.get_for_model"
        ) as mock_get_for_model:
            mock_content_type = Mock(spec=ContentType)
            mock_content_type.get_source_expressions = Mock(return_value=[])
            mock_get_for_model.return_value = mock_content_type

            # Mock the context instance and its save method
            with patch.object(Context, "save") as mock_save:
                result = Context.update_data(
                    content, mock_content_object, source=source, save=True
                )

                mock_get_for_model.assert_called_once_with(mock_content_object)
                mock_get.assert_called_once_with(
                    entity_type=mock_content_type,
                    entity_id=1,
                    source=source,
                )
                mock_init.assert_called_once_with(
                    entity_type=mock_content_type,
                    entity_id=1,
                    source=source,
                )
                assert result.content == content
                mock_save.assert_called_once()

    @patch("apps.ai.models.context.Context.objects.get")
    @patch("apps.ai.models.context.Context.__init__")
    def test_update_data_new_context_without_save(self, mock_init, mock_get):
        """Test update_data creating a new context with save=False."""
        mock_get.side_effect = Context.DoesNotExist
        mock_init.return_value = None  # __init__ should return None

        content = "New test content"
        mock_content_object = Mock()
        mock_content_object.pk = 1
        source = "test_source"

        with patch(
            "apps.ai.models.context.ContentType.objects.get_for_model"
        ) as mock_get_for_model:
            mock_content_type = Mock(spec=ContentType)
            mock_content_type.get_source_expressions = Mock(return_value=[])
            mock_get_for_model.return_value = mock_content_type

            # Mock the context instance and its save method
            with patch.object(Context, "save") as mock_save:
                result = Context.update_data(
                    content, mock_content_object, source=source, save=False
                )

                mock_get_for_model.assert_called_once_with(mock_content_object)
                mock_get.assert_called_once_with(
                    entity_type=mock_content_type,
                    entity_id=1,
                    source=source,
                )
                mock_init.assert_called_once_with(
                    entity_type=mock_content_type,
                    entity_id=1,
                    source=source,
                )
                assert result.content == content
                mock_save.assert_not_called()
