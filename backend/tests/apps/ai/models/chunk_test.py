from unittest.mock import Mock, patch

from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context


def create_model_mock(model_class):
    mock = Mock(spec=model_class)
    mock._state = Mock()
    mock.pk = 1
    mock.id = 1
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

        mock_context = Mock(spec=Context)
        mock_context._state = Mock()
        text = "Test chunk content"
        embedding = [0.1, 0.2, 0.3]

        mock_filter = mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=False)),
        )

        result = Chunk.update_data(text=text, context=mock_context, embedding=embedding, save=True)

        mock_filter.assert_called_once_with(context=mock_context, text=text)
        mock_init.assert_called_once_with(
            context=mock_context,
            text=text,
            embedding=embedding,
        )
        mock_save.assert_called_once()

        assert result is not None
        assert isinstance(result, Chunk)

    def test_update_data_existing_chunk(self, mocker):
        mock_context = Mock(spec=Context)
        mock_context._state = Mock()
        text = "Existing chunk content"
        embedding = [0.1, 0.2, 0.3]

        mock_filter = mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=True)),
        )

        result = Chunk.update_data(text=text, context=mock_context, embedding=embedding, save=True)

        mock_filter.assert_called_once_with(context=mock_context, text=text)
        assert result is None

    @patch("apps.ai.models.chunk.Chunk.save")
    @patch("apps.ai.models.chunk.Chunk.__init__")
    def test_update_data_no_save(self, mock_init, mock_save, mocker):
        mock_init.return_value = None

        mock_context = Mock(spec=Context)
        mock_context._state = Mock()
        text = "Test chunk content"
        embedding = [0.1, 0.2, 0.3]

        mock_filter = mocker.patch(
            "apps.ai.models.chunk.Chunk.objects.filter",
            return_value=Mock(exists=Mock(return_value=False)),
        )

        result = Chunk.update_data(
            text=text, context=mock_context, embedding=embedding, save=False
        )

        mock_filter.assert_called_once_with(context=mock_context, text=text)
        mock_init.assert_called_once_with(
            context=mock_context,
            text=text,
            embedding=embedding,
        )
        mock_save.assert_not_called()

        assert result is not None
        assert isinstance(result, Chunk)

    def test_meta_class_attributes(self):
        assert Chunk._meta.db_table == "ai_chunks"
        assert Chunk._meta.verbose_name == "Chunk"
        assert ("context", "text") in Chunk._meta.unique_together

    def test_context_relationship(self):
        context_field = Chunk._meta.get_field("context")
        from apps.ai.models.context import Context

        assert context_field.related_model == Context
        assert context_field.null is True
        assert context_field.blank is True
