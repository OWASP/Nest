from unittest.mock import MagicMock, patch

from apps.ai.common.utils import create_chunks_and_embeddings


class MockEmbeddingData:
    def __init__(self, embedding):
        self.embedding = embedding


class TestUtils:
    @patch("apps.ai.common.utils.Chunk.update_data")
    @patch("apps.ai.common.utils.time.sleep")
    def test_create_chunks_and_embeddings_success(self, mock_sleep, mock_update_data):
        """Tests the successful path where the OpenAI API returns embeddings."""
        mock_openai_client = MagicMock()
        mock_api_response = MagicMock()
        mock_api_response.data = [
            MockEmbeddingData([0.1, 0.2]),
            MockEmbeddingData([0.3, 0.4]),
        ]
        mock_openai_client.embeddings.create.return_value = mock_api_response

        mock_update_data.return_value = "mock_chunk_instance"

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

        assert mock_update_data.call_count == 2
        mock_update_data.assert_any_call(
            text="first chunk",
            content_object=mock_content_object,
            embedding=[0.1, 0.2],
            save=False,
        )

        assert result == ["mock_chunk_instance", "mock_chunk_instance"]

        mock_sleep.assert_not_called()

    @patch("apps.ai.common.utils.logger")
    def test_create_chunks_and_embeddings_api_error(self, mock_logger):
        """Tests the failure path where the OpenAI API raises an exception."""
        mock_openai_client = MagicMock()
        mock_openai_client.embeddings.create.side_effect = Exception("API connection failed")

        result = create_chunks_and_embeddings(
            all_chunk_texts=["some text"],
            content_object=MagicMock(),
            openai_client=mock_openai_client,
        )

        mock_logger.exception.assert_called_once_with("OpenAI API error")

        assert result == []
