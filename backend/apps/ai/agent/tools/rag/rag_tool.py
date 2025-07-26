"""A tool for orchestrating the components of RAG process."""

import logging

from apps.ai.common.constants import DEFAULT_CHUNKS_RETRIEVAL_LIMIT, DEFAULT_SIMILARITY_THRESHOLD

from .generator import Generator
from .retriever import Retriever

logger = logging.getLogger(__name__)


class RagTool:
    """Main RAG tool that orchestrates the retrieval and generation process."""

    def __init__(
        self,
        embedding_model: str = "text-embedding-3-small",
        chat_model: str = "gpt-4o",
    ):
        """Initialize the RAG tool.

        Args:
            embedding_model (str, optional): The model to use for embeddings.
            chat_model (str, optional): The model to use for chat generation.

        Raises:
            ValueError: If the OpenAI API key is not set.

        """
        try:
            self.retriever = Retriever(embedding_model=embedding_model)
            self.generator = Generator(chat_model=chat_model)
        except Exception:
            logger.exception("Failed to initialize RAG tool")
            raise

    def query(
        self,
        question: str,
        limit: int = DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        content_types: list[str] | None = None,
    ) -> str:
        """Process a user query using the complete RAG pipeline.

        Args:
            question (str): The user's question.
            limit (int): Maximum number of context chunks to retrieve.
            similarity_threshold (float): Minimum similarity score for retrieval.
            content_types (Optional[list[str]]): Content types to filter by.

        Returns:
            dict[str, Any]: A dictionary containing:
                - answer (str): The generated answer

        """
        logger.info("Retrieving context for query")
        retrieved_chunks = self.retriever.retrieve(
            query=question,
            limit=limit,
            similarity_threshold=similarity_threshold,
            content_types=content_types,
        )

        generation_result = self.generator.generate_answer(
            query=question, context_chunks=retrieved_chunks
        )

        logger.info("Successfully processed RAG query")

        return generation_result
