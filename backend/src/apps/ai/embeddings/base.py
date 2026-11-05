"""Abstract base class for embedding providers."""

from abc import ABC, abstractmethod


class Embedder(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query string.

        Args:
            text: The query text to embed.

        Returns:
            List of floats representing the embedding vector.

        """

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.

        """

    @abstractmethod
    def get_dimensions(self) -> int:
        """Get the dimension of embeddings produced by this embedder.

        Returns:
            Integer representing the embedding dimension.

        """
