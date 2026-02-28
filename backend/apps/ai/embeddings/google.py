"""Google implementation of embedder."""

from __future__ import annotations

import math

from django.conf import settings
from google import genai
from google.genai.types import HttpOptions

from apps.ai.embeddings.base import Embedder


class GoogleEmbedder(Embedder):
    """Google implementation of embedder."""

    def __init__(self, model: str = "gemini-embedding-001") -> None:
        """Initialize Google embedder.

        Args:
            model: The Google embedding model to use.

        """
        if not settings.GOOGLE_API_KEY:
            msg = "GOOGLE_API_KEY is required but not set"
            raise ValueError(msg)
        self.client = genai.Client(
            api_key=settings.GOOGLE_API_KEY,
            http_options=HttpOptions(timeout=30 * 1000),
        )
        self.model = model
        self._dimensions = 1536  # gemini-embedding-001 dimensions

    def _normalize_embedding(self, embedding: list[float]) -> list[float]:
        """Normalize embedding vector to unit length (L2 norm).

        Only 3072-dimension embeddings from gemini-embedding-001 are pre-normalized.
        For 1536 dimensions, we must normalize manually for accurate cosine similarity.

        Args:
            embedding: The embedding vector to normalize.

        Returns:
            Normalized embedding vector with unit length.

        """
        return (
            embedding
            if (norm := math.sqrt(sum(x * x for x in embedding))) == 0
            else [x / norm for x in embedding]
        )

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query string.

        Args:
            text: The query text to embed.

        Returns:
            List of floats representing the embedding vector.

        """
        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config={"output_dimensionality": self._dimensions},
        )
        return self._normalize_embedding(result.embeddings[0].values)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.

        """
        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config={"output_dimensionality": self._dimensions},
        )
        return [self._normalize_embedding(e.values) for e in result.embeddings]

    def get_dimensions(self) -> int:
        """Get the dimension of embeddings produced by this embedder.

        Returns:
            Integer representing the embedding dimension.

        """
        return self._dimensions
