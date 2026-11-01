"""OpenAI implementation of embedder."""

from __future__ import annotations

import openai
from django.conf import settings

from apps.ai.embeddings.base import Embedder


class OpenAIEmbedder(Embedder):
    """OpenAI implementation of embedder."""

    def __init__(self, model: str = "text-embedding-3-small") -> None:
        """Initialize OpenAI embedder.

        Args:
            model: The OpenAI embedding model to use.

        """
        self.client = openai.OpenAI(
            api_key=settings.OPEN_AI_SECRET_KEY,
            timeout=30,
        )
        self.model = model
        self._dimensions = 1536  # text-embedding-3-small dimensions

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query string.

        Args:
            text: The query text to embed.

        Returns:
            List of floats representing the embedding vector.

        """
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.

        """
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def get_dimensions(self) -> int:
        """Get the dimension of embeddings produced by this embedder.

        Returns:
            Integer representing the embedding dimension.

        """
        return self._dimensions
