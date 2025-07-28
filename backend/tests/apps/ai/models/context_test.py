"""Unit tests for AI app context model."""

from unittest.mock import Mock, patch

import pytest

from apps.ai.models.context import Context


def create_model_mock(model_class):
    mock = Mock(spec=model_class)
    mock._state = Mock()
    mock.pk = 1
    mock.id = 1
    return mock


class TestContextModel:
    def test_str_method_without_content_type(self):
        context = Context()
        context.id = 1
        context.generated_text = "Sample text without content type"
        context.content_type = None
        context.content_object = None

        result = str(context)

        assert result == "None None: Sample text without content type"

    def test_str_method_with_text_truncation(self):
        long_text = "A" * 100

        context = Context()
        context.id = 1
        context.generated_text = long_text
        context.content_type = None
        context.content_object = None

        result = str(context)

        assert result == f"None None: {long_text[:50]}"
        assert len(result.split(": ", 1)[1]) == 50

    def test_str_method_with_exactly_50_chars(self):
        text_50_chars = "A" * 50

        context = Context()
        context.id = 1
        context.generated_text = text_50_chars
        context.content_type = None
        context.content_object = None

        result = str(context)

        assert result == f"None None: {text_50_chars}"
        assert len(result.split(": ", 1)[1]) == 50

    def test_str_method_with_empty_text(self):
        context = Context()
        context.id = 1
        context.generated_text = ""
        context.content_type = None
        context.content_object = None

        result = str(context)

        assert result == "None None: "

    def test_meta_class_attributes(self):
        assert Context._meta.db_table == "ai_contexts"
        assert Context._meta.verbose_name == "Context"

    def test_generated_text_field_properties(self):
        field = Context._meta.get_field("generated_text")
        assert field.verbose_name == "Generated Text"
        assert field.__class__.__name__ == "TextField"

    def test_content_type_field_properties(self):
        field = Context._meta.get_field("content_type")
        assert field.null is True
        assert field.blank is True
        assert hasattr(field, "remote_field")
        assert field.remote_field.on_delete.__name__ == "CASCADE"

    def test_object_id_field_properties(self):
        field = Context._meta.get_field("object_id")
        assert field.default == 0
        assert field.__class__.__name__ == "PositiveIntegerField"

    def test_source_field_properties(self):
        field = Context._meta.get_field("source")
        assert field.max_length == 100
        assert field.blank is True
        assert field.default == ""

    def test_content_object_generic_foreign_key(self):
        field = Context._meta.get_field("content_object")
        assert field.__class__.__name__ == "GenericForeignKey"
        assert field.ct_field == "content_type"
        assert field.fk_field == "object_id"

    @patch("apps.ai.models.context.Context.save")
    @patch("apps.ai.models.context.Context.__init__")
    def test_context_creation_with_save(self, mock_init, mock_save):
        mock_init.return_value = None

        generated_text = "Test generated text"
        source = "test_source"

        context = Context(generated_text=generated_text, source=source)
        context.save()

        mock_save.assert_called_once()

    def test_context_inheritance_from_timestamped_model(self):
        from apps.common.models import TimestampedModel

        assert issubclass(Context, TimestampedModel)

    @patch("apps.ai.models.context.Context.objects.create")
    def test_context_manager_create(self, mock_create):
        mock_context = create_model_mock(Context)
        mock_create.return_value = mock_context

        generated_text = "Test text"
        source = "test_source"

        result = Context.objects.create(generated_text=generated_text, source=source)

        mock_create.assert_called_once_with(generated_text=generated_text, source=source)
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
        context.generated_text = "Valid text"
        context.source = "A" * 100

        context.full_clean()

        mock_full_clean.assert_called_once()

    @patch("apps.ai.models.context.Context.full_clean")
    def test_context_validation_source_too_long(self, mock_full_clean):
        from django.core.exceptions import ValidationError

        mock_full_clean.side_effect = ValidationError("Source too long")

        context = Context()
        context.generated_text = "Valid text"
        context.source = "A" * 101

        with pytest.raises(ValidationError) as exc_info:
            context.full_clean()
        assert "Source too long" in str(exc_info.value)

    def test_context_default_values(self):
        context = Context()

        assert context.object_id == 0
        assert context.source == ""
        assert context.content_type is None
        assert context.content_object is None

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
