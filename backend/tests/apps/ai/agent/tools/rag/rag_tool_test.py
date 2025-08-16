"""Tests for the RAG Tool."""

import os
from unittest.mock import MagicMock, patch

import pytest

from apps.ai.agent.tools.rag.rag_tool import RagTool


class TestRagTool:
    """Test cases for the RagTool class."""

    def test_init_success(self):
        """Test successful initialization of RagTool."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("apps.ai.agent.tools.rag.rag_tool.Retriever") as mock_retriever_class,
            patch("apps.ai.agent.tools.rag.rag_tool.Generator") as mock_generator_class,
        ):
            mock_retriever = MagicMock()
            mock_generator = MagicMock()
            mock_retriever_class.return_value = mock_retriever
            mock_generator_class.return_value = mock_generator

            rag_tool = RagTool(
                embedding_model="custom-embedding-model", chat_model="custom-chat-model"
            )

            assert rag_tool.retriever == mock_retriever
            assert rag_tool.generator == mock_generator
            mock_retriever_class.assert_called_once_with(embedding_model="custom-embedding-model")
            mock_generator_class.assert_called_once_with(chat_model="custom-chat-model")

    def test_init_default_models(self):
        """Test initialization with default model parameters."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("apps.ai.agent.tools.rag.rag_tool.Retriever") as mock_retriever_class,
            patch("apps.ai.agent.tools.rag.rag_tool.Generator") as mock_generator_class,
        ):
            mock_retriever = MagicMock()
            mock_generator = MagicMock()
            mock_retriever_class.return_value = mock_retriever
            mock_generator_class.return_value = mock_generator

            RagTool()

            mock_retriever_class.assert_called_once_with(embedding_model="text-embedding-3-small")
            mock_generator_class.assert_called_once_with(chat_model="gpt-4o")

    def test_init_no_api_key(self):
        """Test initialization fails when API key is not set."""
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("apps.ai.agent.tools.rag.rag_tool.Retriever") as mock_retriever_class,
        ):
            mock_retriever_class.side_effect = ValueError(
                "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            )

            with pytest.raises(
                ValueError,
                match="DJANGO_OPEN_AI_SECRET_KEY environment variable not set",
            ):
                RagTool()

    def test_query_success(self):
        """Test successful query execution."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("apps.ai.agent.tools.rag.rag_tool.Retriever") as mock_retriever_class,
            patch("apps.ai.agent.tools.rag.rag_tool.Generator") as mock_generator_class,
        ):
            mock_retriever = MagicMock()
            mock_generator = MagicMock()
            mock_retriever_class.return_value = mock_retriever
            mock_generator_class.return_value = mock_generator

            mock_chunks = [{"text": "Test content", "source_name": "Test Source"}]
            mock_retriever.retrieve.return_value = mock_chunks
            mock_generator.generate_answer.return_value = "Generated answer"

            rag_tool = RagTool()

            result = rag_tool.query(
                question="What is OWASP?",
                content_types=["chapter"],
                limit=10,
                similarity_threshold=0.5,
            )

            assert result == "Generated answer"
            mock_retriever.retrieve.assert_called_once_with(
                content_types=["chapter"],
                limit=10,
                query="What is OWASP?",
                similarity_threshold=0.5,
            )
            mock_generator.generate_answer.assert_called_once_with(
                context_chunks=mock_chunks, query="What is OWASP?"
            )

    def test_query_with_defaults(self):
        """Test query with default parameters."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("apps.ai.agent.tools.rag.rag_tool.Retriever") as mock_retriever_class,
            patch("apps.ai.agent.tools.rag.rag_tool.Generator") as mock_generator_class,
        ):
            mock_retriever = MagicMock()
            mock_generator = MagicMock()
            mock_retriever_class.return_value = mock_retriever
            mock_generator_class.return_value = mock_generator

            mock_chunks = []
            mock_retriever.retrieve.return_value = mock_chunks
            mock_generator.generate_answer.return_value = "Default answer"

            rag_tool = RagTool()

            result = rag_tool.query("Test question")

            assert result == "Default answer"
            mock_retriever.retrieve.assert_called_once_with(
                content_types=None,
                limit=5,
                query="Test question",
                similarity_threshold=0.4,
            )

    def test_query_empty_content_types(self):
        """Test query with empty content types list."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("apps.ai.agent.tools.rag.rag_tool.Retriever") as mock_retriever_class,
            patch("apps.ai.agent.tools.rag.rag_tool.Generator") as mock_generator_class,
        ):
            mock_retriever = MagicMock()
            mock_generator = MagicMock()
            mock_retriever_class.return_value = mock_retriever
            mock_generator_class.return_value = mock_generator

            mock_chunks = []
            mock_retriever.retrieve.return_value = mock_chunks
            mock_generator.generate_answer.return_value = "Answer"

            rag_tool = RagTool()

            result = rag_tool.query("Test question", content_types=[])

            assert result == "Answer"
            mock_retriever.retrieve.assert_called_once_with(
                content_types=[],
                limit=5,
                query="Test question",
                similarity_threshold=0.4,
            )

    @patch("apps.ai.agent.tools.rag.rag_tool.logger")
    def test_query_logs_retrieval(self, mock_logger):
        """Test that query logs the retrieval process."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("apps.ai.agent.tools.rag.rag_tool.Retriever") as mock_retriever_class,
            patch("apps.ai.agent.tools.rag.rag_tool.Generator") as mock_generator_class,
        ):
            mock_retriever = MagicMock()
            mock_generator = MagicMock()
            mock_retriever_class.return_value = mock_retriever
            mock_generator_class.return_value = mock_generator

            mock_retriever.retrieve.return_value = []
            mock_generator.generate_answer.return_value = "Answer"

            rag_tool = RagTool()
            rag_tool.query("Test question")

            mock_logger.info.assert_called_once_with("Retrieving context for query")
