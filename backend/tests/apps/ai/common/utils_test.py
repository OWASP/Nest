from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, call, patch

import openai

from apps.ai.common.utils import create_chunks_and_embeddings


class MockEmbeddingData:
    def __init__(self, embedding):
        self.embedding = embedding


class TestUtils:
    @patch("apps.ai.common.utils.Context")
    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.time.sleep")
    @patch("apps.ai.common.utils.datetime")
    def test_create_chunks_and_embeddings_success(
        self, mock_datetime, mock_sleep, mock_update_data, mock_context
    ):
        """Tests the successful path where the OpenAI API returns embeddings."""
        base_time = datetime.now(UTC)
        mock_datetime.now.return_value = base_time
        mock_datetime.UTC = UTC
        mock_datetime.timedelta = timedelta

        mock_openai_client = MagicMock()
        mock_api_response = MagicMock()
        mock_api_response.data = [
            MockEmbeddingData([0.1, 0.2]),
            MockEmbeddingData([0.3, 0.4]),
        ]
        mock_openai_client.embeddings.create.return_value = mock_api_response

        # Create mock chunk instances with .save method
        mock_chunk1 = MagicMock()
        mock_chunk2 = MagicMock()
        mock_update_data.side_effect = [mock_chunk1, mock_chunk2]

        all_chunk_texts = ["first chunk", "second chunk"]
        mock_content_object = MagicMock()

        result = create_chunks_and_embeddings(
            all_chunk_texts,
            mock_content_object,
            mock_openai_client,
        )

        mock_openai_client.embeddings.create.assert_called_once_with(
            input=all_chunk_texts,
            model="text-embedding-3-small",
        )

        mock_update_data.assert_has_calls(
            [
                call(text="first chunk", embedding=[0.1, 0.2], save=False),
                call(text="second chunk", embedding=[0.3, 0.4], save=False),
            ]
        )

        assert mock_chunk1.context == mock_content_object
        assert mock_chunk2.context == mock_content_object

        mock_chunk1.save.assert_called_once()
        mock_chunk2.save.assert_called_once()

        assert result == [mock_chunk1, mock_chunk2]

        mock_sleep.assert_not_called()

    @patch("apps.ai.common.utils.logger")
    def test_create_chunks_and_embeddings_api_error(self, mock_logger):
        """Tests the failure path where the OpenAI API raises an exception."""
        mock_openai_client = MagicMock()

        mock_openai_client.embeddings.create.side_effect = openai.OpenAIError(
            "API connection failed"
        )

        result = create_chunks_and_embeddings(
            chunk_texts=["some text"],
            context=MagicMock(),
            openai_client=mock_openai_client,
        )

        mock_logger.exception.assert_called_once_with("Failed to create chunks and embeddings")

        assert result == []

    @patch("apps.ai.common.utils.Context")
    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.time.sleep")
    @patch("apps.ai.common.utils.datetime")
    def test_create_chunks_and_embeddings_no_sleep_with_current_settings(
        self, mock_datetime, mock_sleep, mock_update_data, mock_context
    ):
        """Tests that sleep is not called with current offset settings."""
        base_time = datetime.now(UTC)
        mock_datetime.now.return_value = base_time
        mock_datetime.UTC = UTC
        mock_datetime.timedelta = timedelta

        mock_openai_client = MagicMock()
        mock_api_response = MagicMock()
        mock_api_response.data = [MockEmbeddingData([0.1, 0.2])]
        mock_openai_client.embeddings.create.return_value = mock_api_response

        mock_chunk = MagicMock()
        mock_update_data.return_value = mock_chunk

        result = create_chunks_and_embeddings(
            ["test chunk"],
            MagicMock(),
            mock_openai_client,
        )

        mock_sleep.assert_not_called()
        mock_chunk.save.assert_called_once()
        assert result == [mock_chunk]
