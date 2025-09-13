from unittest.mock import Mock, patch

import pytest

from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context


@pytest.fixture
def mock_context():
    mock = Mock(spec=Context)
    mock.id = 1
    mock.entity_type = Mock()
    mock.entity_id = 1
    return mock


class TestChunkModel:
    def test_str_method(self):
        mock_context = Mock(spec=Context)
        mock_context.__str__ = Mock(return_value="Context 1 for message Test Message: ...")
        mock_context._state = Mock()
        chunk = Chunk()
        chunk.id = 1
        chunk.text = "This is a test chunk with some content that should be displayed"
        chunk.context = mock_context
        result = str(chunk)
        assert "Chunk 1 for Context 1 for message Test Message:" in result
        assert "This is a test chunk with some content that" in result

    def test_bulk_save_with_chunks(self):
        mock_chunks = [Mock(spec=Chunk), Mock(spec=Chunk), Mock(spec=Chunk)]
        for chunk in mock_chunks:
            chunk.context = Mock()
            chunk.text = "test text"

        with patch("apps.ai.models.chunk.Chunk.objects.filter") as mock_filter:
            mock_filter.return_value.exists.return_value = False
            with patch("apps.common.models.BulkSaveModel.bulk_save") as mock_bulk_save:
                Chunk.bulk_save(mock_chunks)
                mock_bulk_save.assert_called_once_with(Chunk, mock_chunks, fields=None)

    def test_bulk_save_with_fields_parameter(self):
        mock_chunks = [Mock(spec=Chunk), Mock(spec=Chunk)]
        for chunk in mock_chunks:
            chunk.context = Mock()
            chunk.text = "test text"
        fields = ["text", "embedding"]

        with patch("apps.ai.models.chunk.Chunk.objects.filter") as mock_filter:
            mock_filter.return_value.exists.return_value = False
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
    def test_update_data_save_with_context(self, mock_save):
        text = "Test chunk content"
        embedding = [0.1, 0.2, 0.3]
        mock_context = Mock(spec=Context)

        with patch("apps.ai.models.chunk.Chunk") as mock_chunk:
            chunk_instance = Mock()
            chunk_instance.context_id = 123
            mock_chunk.return_value = chunk_instance
            mock_chunk.objects.filter.return_value.exists.return_value = False

            result = Chunk.update_data(
                text=text, embedding=embedding, context=mock_context, save=True
            )

            mock_chunk.assert_called_once_with(
                text=text, embedding=embedding, context=mock_context
            )
            chunk_instance.save.assert_called_once()
            assert result is chunk_instance

    def test_update_data_creates_new_chunk_and_saves(self, mock_context):
        """Test that a new chunk is created and saved."""
        text = "New unique chunk content"
        embedding = [0.1, 0.2, 0.3]

        with patch("apps.ai.models.chunk.Chunk") as mock_chunk_class:
            mock_chunk_class.objects.filter.return_value.exists.return_value = False
            mock_instance = Mock(spec=Chunk)
            mock_chunk_class.return_value = mock_instance

            result = Chunk.update_data(
                text=text, embedding=embedding, context=mock_context, save=True
            )

            mock_chunk_class.objects.filter.assert_called_once_with(
                context=mock_context,
                text=text,
            )
            mock_chunk_class.assert_called_once_with(
                text=text, embedding=embedding, context=mock_context
            )
            mock_instance.save.assert_called_once()
            assert result is mock_instance

    def test_update_data_creates_new_chunk_no_save(self, mock_context):
        """Test that a new chunk is created but NOT saved when save=False."""
        text = "New unique chunk content"
        embedding = [0.1, 0.2, 0.3]

        with patch("apps.ai.models.chunk.Chunk") as mock_chunk_class:
            mock_chunk_class.objects.filter.return_value.exists.return_value = False
            mock_instance = Mock(spec=Chunk)
            mock_chunk_class.return_value = mock_instance

            result = Chunk.update_data(
                text=text, embedding=embedding, context=mock_context, save=False
            )

            mock_chunk_class.objects.filter.assert_called_once_with(
                context=mock_context,
                text=text,
            )
            mock_chunk_class.assert_called_once_with(
                text=text, embedding=embedding, context=mock_context
            )
            mock_instance.save.assert_not_called()
            assert result is mock_instance

    def test_update_data_returns_none_if_chunk_already_exists(self, mock_context):
        """Test that update_data returns None when a chunk with the same text."""
        text = "Existing chunk content"
        embedding = [0.1, 0.2, 0.3]

        with patch("apps.ai.models.chunk.Chunk") as mock_chunk_class:
            mock_chunk_class.objects.filter.return_value.exists.return_value = True

            result = Chunk.update_data(
                text=text, embedding=embedding, context=mock_context, save=True
            )

            mock_chunk_class.objects.filter.assert_called_once_with(
                context=mock_context,
                text=text,
            )

            mock_chunk_class.assert_not_called()
            assert result is None

    def test_meta_class_attributes(self):
        assert Chunk._meta.db_table == "ai_chunks"
        assert Chunk._meta.verbose_name == "Chunk"
        assert ("context", "text") in Chunk._meta.unique_together

    def test_context_relationship(self):
        context_field = Chunk._meta.get_field("context")
        from apps.ai.models.context import Context

        assert context_field.related_model == Context
