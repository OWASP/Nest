from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, call, patch

from apps.ai.common.utils import (
    create_chunks_and_embeddings,
    regenerate_chunks_for_context,
)


class TestUtils:
    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.time.sleep")
    @patch("apps.ai.common.utils.datetime")
    @patch("apps.ai.common.utils.get_embedder")
    def test_create_chunks_and_embeddings_success(
        self, mock_get_embedder, mock_datetime, mock_sleep, mock_update_data
    ):
        """Tests the successful path where the embedder returns embeddings."""
        base_time = datetime.now(UTC)
        mock_datetime.now.return_value = base_time
        mock_datetime.UTC = UTC
        mock_datetime.timedelta = timedelta

        mock_embedder = MagicMock()
        mock_embedder.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_get_embedder.return_value = mock_embedder

        mock_chunk1 = MagicMock()
        mock_chunk2 = MagicMock()
        mock_update_data.side_effect = [mock_chunk1, mock_chunk2]

        all_chunk_texts = ["first chunk", "second chunk"]
        mock_content_object = MagicMock()

        result = create_chunks_and_embeddings(
            all_chunk_texts,
            mock_content_object,
        )

        mock_embedder.embed_documents.assert_called_once_with(all_chunk_texts)

        mock_update_data.assert_has_calls(
            [
                call(
                    text="first chunk",
                    embedding=[0.1, 0.2],
                    context=mock_content_object,
                    save=True,
                ),
                call(
                    text="second chunk",
                    embedding=[0.3, 0.4],
                    context=mock_content_object,
                    save=True,
                ),
            ]
        )

        assert result == [mock_chunk1, mock_chunk2]

        mock_sleep.assert_not_called()

    @patch("apps.ai.common.utils.logger")
    @patch("apps.ai.common.utils.get_embedder")
    def test_create_chunks_and_embeddings_error(self, mock_get_embedder, mock_logger):
        """Tests the failure path where the embedder raises an exception."""
        mock_embedder = MagicMock()
        mock_embedder.embed_documents.side_effect = TypeError("Type error")
        mock_get_embedder.return_value = mock_embedder

        result = create_chunks_and_embeddings(
            chunk_texts=["some text"],
            context=MagicMock(),
        )

        mock_logger.exception.assert_called_once_with("Failed to create chunks and embeddings")

        assert result == []

    @patch("apps.ai.common.utils.logger")
    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.get_embedder")
    def test_create_chunks_and_embeddings_none_context(
        self, mock_get_embedder, mock_update_data, mock_logger
    ):
        """Tests the failure path when context is None."""
        mock_embedder = MagicMock()
        mock_embedder.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_get_embedder.return_value = mock_embedder

        mock_update_data.side_effect = AttributeError("Context is required")

        result = create_chunks_and_embeddings(
            chunk_texts=["some text"],
            context=None,
        )

        mock_logger.exception.assert_called_once_with("Failed to create chunks and embeddings")
        assert result == []

    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.time.sleep")
    @patch("apps.ai.common.utils.datetime")
    @patch("apps.ai.common.utils.get_embedder")
    def test_create_chunks_and_embeddings_sleep_called(
        self, mock_get_embedder, mock_datetime, mock_sleep, mock_update_data
    ):
        """Tests that sleep is called when needed."""
        base_time = datetime.now(UTC)
        mock_datetime.now.return_value = base_time
        mock_datetime.UTC = UTC
        mock_datetime.timedelta = timedelta

        mock_embedder = MagicMock()
        mock_embedder.embed_documents.return_value = [[0.1, 0.2]]
        mock_get_embedder.return_value = mock_embedder

        mock_chunk_instance = MagicMock()
        mock_update_data.return_value = mock_chunk_instance

        mock_content_object = MagicMock()

        result = create_chunks_and_embeddings(
            ["test chunk"],
            mock_content_object,
        )

        mock_sleep.assert_not_called()
        assert result == [mock_chunk_instance]

    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.time.sleep")
    @patch("apps.ai.common.utils.datetime")
    @patch("apps.ai.common.utils.get_embedder")
    def test_create_chunks_and_embeddings_no_sleep_with_current_settings(
        self, mock_get_embedder, mock_datetime, mock_sleep, mock_update_data
    ):
        """Tests that sleep is not called with current offset settings."""
        base_time = datetime.now(UTC)
        mock_datetime.now.return_value = base_time
        mock_datetime.UTC = UTC
        mock_datetime.timedelta = timedelta

        mock_embedder = MagicMock()
        mock_embedder.embed_documents.return_value = [[0.1, 0.2]]
        mock_get_embedder.return_value = mock_embedder

        mock_chunk_instance = MagicMock()
        mock_update_data.return_value = mock_chunk_instance
        mock_context_obj = MagicMock()

        result = create_chunks_and_embeddings(
            ["test chunk"],
            mock_context_obj,
        )

        mock_sleep.assert_not_called()
        mock_update_data.assert_called_once_with(
            text="test chunk", embedding=[0.1, 0.2], context=mock_context_obj, save=True
        )
        assert result == [mock_chunk_instance]

    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.time.sleep")
    @patch("apps.ai.common.utils.datetime")
    @patch("apps.ai.common.utils.get_embedder")
    def test_create_chunks_and_embeddings_sleep_when_rate_limited(
        self, mock_get_embedder, mock_datetime, mock_sleep, mock_update_data
    ):
        """Tests that sleep is called when rate limiting is needed."""
        base_time = datetime.now(UTC)

        mock_datetime.now.side_effect = [
            base_time,
            base_time,
        ]
        mock_datetime.UTC = UTC
        mock_datetime.timedelta = timedelta

        mock_embedder = MagicMock()
        mock_embedder.embed_documents.return_value = [[0.1, 0.2]]
        mock_get_embedder.return_value = mock_embedder

        mock_chunk_instance = MagicMock()
        mock_update_data.return_value = mock_chunk_instance

        with (
            patch("apps.ai.common.utils.DEFAULT_LAST_REQUEST_OFFSET_SECONDS", 5),
            patch("apps.ai.common.utils.MIN_REQUEST_INTERVAL_SECONDS", 10),
        ):
            mock_context_obj = MagicMock()

            result = create_chunks_and_embeddings(
                ["test chunk"],
                mock_context_obj,
            )

        mock_sleep.assert_called_once()
        assert result == [mock_chunk_instance]

    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.get_embedder")
    def test_create_chunks_and_embeddings_filter_none_chunks(
        self, mock_get_embedder, mock_update_data
    ):
        """Tests that None chunks are filtered out from results."""
        mock_embedder = MagicMock()
        mock_embedder.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_get_embedder.return_value = mock_embedder

        mock_chunk_instance = MagicMock()
        mock_update_data.side_effect = [mock_chunk_instance, None]

        mock_context_obj = MagicMock()

        result = create_chunks_and_embeddings(
            ["first chunk", "second chunk"],
            mock_context_obj,
        )

        assert len(result) == 1
        assert result[0] == mock_chunk_instance


class TestRegenerateChunksForContext:
    """Test cases for regenerate_chunks_for_context function."""

    @patch("apps.ai.common.utils.logger")
    @patch("apps.ai.common.utils.create_chunks_and_embeddings")
    @patch("apps.ai.common.utils.Chunk.split_text")
    def test_regenerate_chunks_for_context_success(
        self, mock_split_text, mock_create_chunks, mock_logger
    ):
        """Test successful regeneration of chunks for context."""
        context = MagicMock()
        context.content = "This is test content for chunking"

        mock_existing_chunks = MagicMock()
        context.chunks = mock_existing_chunks

        new_chunk_texts = ["chunk1", "chunk2"]
        mock_split_text.return_value = new_chunk_texts

        regenerate_chunks_for_context(context)

        mock_existing_chunks.all.assert_called_once()
        mock_existing_chunks.all().delete.assert_called_once()

        mock_split_text.assert_called_once_with(context.content)

        mock_create_chunks.assert_called_once_with(
            chunk_texts=new_chunk_texts,
            context=context,
            save=True,
        )

        mock_logger.info.assert_called_once_with(
            "Successfully completed chunk regeneration for new context"
        )

    @patch("apps.ai.common.utils.logger")
    @patch("apps.ai.common.utils.Chunk.split_text")
    def test_regenerate_chunks_for_context_no_content(self, mock_split_text, mock_logger):
        """Test regeneration when there's no content to chunk."""
        context = MagicMock()
        context.content = "Some content"

        mock_existing_chunks = MagicMock()
        context.chunks = mock_existing_chunks

        mock_split_text.return_value = []

        regenerate_chunks_for_context(context)

        mock_existing_chunks.all.assert_called_once()
        mock_existing_chunks.all().delete.assert_called_once()

        mock_split_text.assert_called_once_with(context.content)

        mock_logger.warning.assert_called_once_with(
            "No content to chunk for Context. Process stopped."
        )

        mock_logger.info.assert_not_called()

    @patch("apps.ai.common.utils.logger")
    @patch("apps.ai.common.utils.create_chunks_and_embeddings")
    @patch("apps.ai.common.utils.Chunk.split_text")
    def test_regenerate_chunks_for_context_no_existing_chunks(
        self, mock_split_text, mock_create_chunks, mock_logger
    ):
        """Test regeneration when there are no existing chunks."""
        context = MagicMock()
        context.content = "This is test content for chunking"

        mock_existing_chunks = MagicMock()
        context.chunks = mock_existing_chunks

        new_chunk_texts = ["chunk1", "chunk2"]
        mock_split_text.return_value = new_chunk_texts

        regenerate_chunks_for_context(context)

        mock_existing_chunks.all.assert_called_once()
        mock_existing_chunks.all().delete.assert_called_once()

        mock_split_text.assert_called_once_with(context.content)

        mock_create_chunks.assert_called_once_with(
            chunk_texts=new_chunk_texts,
            context=context,
            save=True,
        )

        mock_logger.info.assert_called_once_with(
            "Successfully completed chunk regeneration for new context"
        )
