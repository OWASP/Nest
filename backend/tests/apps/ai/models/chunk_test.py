from unittest.mock import Mock, patch

from django.db import models

from apps.ai.models.chunk import Chunk
from apps.slack.models.message import Message


def create_model_mock(model_class):
    mock = Mock(spec=model_class)
    mock._state = Mock()
    mock.pk = 1
    return mock


class TestChunkModel:
    def test_str_method(self):
        """Test the string representation of a chunk."""
        mock_message = create_model_mock(Message)
        mock_message.slack_message_id = "123456.789"

        chunk = Chunk(
            id=1,
            text="This is a test chunk with some content that should be displayed",
            message=mock_message,
        )

        result = str(chunk)
        assert "Chunk 1 for Message 123456.789:" in result
        assert "This is a test chunk with some content that" in result

    def test_bulk_save_with_chunks(self):
        """Test bulk_save method with valid chunks."""
        mock_chunks = [Mock(), Mock(), Mock()]

        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Chunk.bulk_save(mock_chunks)
            mock_bulk_save.assert_called_once_with(Chunk, mock_chunks, fields=None)

    def test_bulk_save_with_fields_parameter(self):
        """Test bulk_save method with custom fields parameter."""
        mock_chunks = [Mock(), Mock()]
        fields = ["text", "embedding"]

        with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
            Chunk.bulk_save(mock_chunks, fields=fields)
            mock_bulk_save.assert_called_once_with(Chunk, mock_chunks, fields=fields)

    def test_update_data_new_chunk(self, mocker):
        """Test update_data method creates new chunk when it doesn't exist."""
        mock_message = create_model_mock(Message)
        text = "Test chunk content"
        embedding = [0.1, 0.2, 0.3]

        mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=False)),
        )

        patched_save = mocker.patch("apps.ai.models.chunk.Chunk.save")

        with patch.object(Chunk, "message", create=True):
            result = Chunk.update_data(
                text=text, message=mock_message, embedding=embedding, save=True
            )

            assert result is not None
            assert isinstance(result, Chunk)
            assert result.text == text
            assert result.message == mock_message
            assert result.embedding == embedding
            patched_save.assert_called_once()

    def test_update_data_existing_chunk(self, mocker):
        """Test update_data method returns None when chunk already exists."""
        mock_message = create_model_mock(Message)
        text = "Existing chunk content"
        embedding = [0.1, 0.2, 0.3]

        mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=True)),
        )

        result = Chunk.update_data(text=text, message=mock_message, embedding=embedding, save=True)

        assert result is None

    def test_update_data_no_save(self, mocker):
        """Test update_data method with save=False."""
        mock_message = create_model_mock(Message)
        text = "Test chunk content"
        embedding = [0.1, 0.2, 0.3]

        mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=False)),
        )

        patched_save = mocker.patch("apps.ai.models.chunk.Chunk.save")

        with patch.object(Chunk, "message", create=True):
            result = Chunk.update_data(
                text=text, message=mock_message, embedding=embedding, save=False
            )

            assert result is not None
            assert isinstance(result, Chunk)
            assert result.text == text
            assert result.message == mock_message
            assert result.embedding == embedding
            patched_save.assert_not_called()

    def test_meta_class_attributes(self):
        """Test the Meta class attributes of the Chunk model."""
        assert Chunk._meta.db_table == "ai_chunks"
        assert Chunk._meta.verbose_name == "Chunk"
        assert ("message", "text") in Chunk._meta.unique_together

    def test_message_foreign_key_relationship(self):
        """Test the foreign key relationship with Message model."""
        message_field = Chunk._meta.get_field("message")

        assert isinstance(message_field, models.ForeignKey)
        assert message_field.remote_field.model == Message
        assert message_field.remote_field.related_name == "chunks"
