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
        self.retriever = Retriever(embedding_model=embedding_model)
        self.generator = Generator(chat_model=chat_model)

    def query(
        self,
        question: str,
        content_types: list[str] | None = None,
        limit: int = DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> str:
        """Process a user query using the complete RAG pipeline.

        Args:
            question (str): The user's question.
            content_types (Optional[list[str]]): Content types to filter by.
            limit (int): Maximum number of context chunks to retrieve.
            similarity_threshold (float): Minimum similarity score for retrieval.

        Returns:
            The generated answer as a string.

        """
        logger.info("Retrieving context for query")

        return self.generator.generate_answer(
            context_chunks=self.retriever.retrieve(
                content_types=content_types,
                limit=limit,
                query=question,
                similarity_threshold=similarity_threshold,
            ),
            query=question,
        )
