from unittest.mock import Mock, patch

from django.contrib.contenttypes.models import ContentType
from django.db import models

from apps.ai.models.chunk import Chunk
from apps.slack.models.message import Message


def create_model_mock(model_class):
    mock = Mock(spec=model_class)
    mock._state = Mock()
    mock.pk = 1
    mock.id = 1
    return mock


class TestChunkModel:
    def test_str_method(self):
        mock_message = create_model_mock(Message)
        mock_message.name = "Test Message"

        mock_content_type = Mock(spec=ContentType)
        mock_content_type.model = "message"

        with (
            patch.object(Chunk, "content_type", mock_content_type),
            patch.object(Chunk, "content_object", mock_message),
        ):
            chunk = Chunk()
            chunk.id = 1
            chunk.text = "This is a test chunk with some content that should be displayed"

            result = str(chunk)
            assert "Chunk 1 for message Test Message:" in result
            assert "This is a test chunk with some content that" in result

    def test_bulk_save_with_chunks(self):
        mock_chunks = [Mock(), Mock(), Mock()]

        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Chunk.bulk_save(mock_chunks)
            mock_bulk_save.assert_called_once_with(Chunk, mock_chunks, fields=None)

    def test_bulk_save_with_fields_parameter(self):
        mock_chunks = [Mock(), Mock()]
        fields = ["text", "embedding"]

        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Chunk.bulk_save(mock_chunks, fields=fields)
            mock_bulk_save.assert_called_once_with(Chunk, mock_chunks, fields=fields)

    def test_split_text(self):
        text = "This is a long text that should be split into multiple chunks. " * 10

        result = Chunk.split_text(text)

        assert isinstance(result, list)
        assert len(result) > 1
        assert all(isinstance(chunk, str) for chunk in result)

    @patch("apps.ai.models.chunk.Chunk.save")
    @patch("apps.ai.models.chunk.Chunk.__init__")
    def test_update_data_new_chunk(self, mock_init, mock_save, mocker):
        mock_init.return_value = None

        mock_message = create_model_mock(Message)
        text = "Test chunk content"
        embedding = [0.1, 0.2, 0.3]

        mock_content_type = Mock(spec=ContentType)
        mock_get_for_model = mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock_content_type,
        )

        mock_filter = mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=False)),
        )

        result = Chunk.update_data(
            text=text, content_object=mock_message, embedding=embedding, save=True
        )

        mock_get_for_model.assert_called_once_with(mock_message)
        mock_filter.assert_called_once_with(
            content_type=mock_content_type, object_id=mock_message.id, text=text
        )
        mock_init.assert_called_once_with(
            content_type=mock_content_type,
            object_id=mock_message.id,
            text=text,
            embedding=embedding,
        )
        mock_save.assert_called_once()

        assert result is not None
        assert isinstance(result, Chunk)

    def test_update_data_existing_chunk(self, mocker):
        mock_message = create_model_mock(Message)
        text = "Existing chunk content"
        embedding = [0.1, 0.2, 0.3]

        mock_content_type = Mock(spec=ContentType)
        mock_get_for_model = mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock_content_type,
        )

        mock_filter = mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=True)),
        )

        result = Chunk.update_data(
            text=text, content_object=mock_message, embedding=embedding, save=True
        )

        mock_get_for_model.assert_called_once_with(mock_message)
        mock_filter.assert_called_once_with(
            content_type=mock_content_type, object_id=mock_message.id, text=text
        )
        assert result is None

    @patch("apps.ai.models.chunk.Chunk.save")
    @patch("apps.ai.models.chunk.Chunk.__init__")
    def test_update_data_no_save(self, mock_init, mock_save, mocker):
        mock_init.return_value = None

        mock_message = create_model_mock(Message)
        text = "Test chunk content"
        embedding = [0.1, 0.2, 0.3]

        mock_content_type = Mock(spec=ContentType)
        mock_get_for_model = mocker.patch(
            "django.contrib.contenttypes.models.ContentType.objects.get_for_model",
            return_value=mock_content_type,
        )

        mock_filter = mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=False)),
        )

        result = Chunk.update_data(
            text=text, content_object=mock_message, embedding=embedding, save=False
        )

        mock_get_for_model.assert_called_once_with(mock_message)
        mock_filter.assert_called_once_with(
            content_type=mock_content_type, object_id=mock_message.id, text=text
        )
        mock_init.assert_called_once_with(
            content_type=mock_content_type,
            object_id=mock_message.id,
            text=text,
            embedding=embedding,
        )
        mock_save.assert_not_called()

        assert result is not None
        assert isinstance(result, Chunk)

    def test_meta_class_attributes(self):
        assert Chunk._meta.db_table == "ai_chunks"
        assert Chunk._meta.verbose_name == "Chunk"
        assert ("content_type", "object_id", "text") in Chunk._meta.unique_together

    def test_generic_foreign_key_relationship(self):
        content_type_field = Chunk._meta.get_field("content_type")
        object_id_field = Chunk._meta.get_field("object_id")

        assert isinstance(content_type_field, models.ForeignKey)
        assert content_type_field.remote_field.model == ContentType
        assert isinstance(object_id_field, models.PositiveIntegerField)
