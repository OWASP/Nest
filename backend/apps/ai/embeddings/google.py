"""Google implementation of embedder."""

from __future__ import annotations

import math

from django.conf import settings
from google import genai

from apps.ai.embeddings.base import Embedder


class GoogleEmbedder(Embedder):
    """Google implementation of embedder."""

    def __init__(self, model: str = "gemini-embedding-001") -> None:
        """Initialize Google embedder.

        Args:
            model: The Google embedding model to use.

        """
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model = model
        self._dimensions = 1536

    def _normalize_embedding(self, embedding: list[float]) -> list[float]:
        """Normalize embedding vector to unit length (L2 norm).

        Only 3072-dimension embeddings from gemini-embedding-001 are pre-normalized.
        For 1536 dimensions, we must normalize manually for accurate cosine similarity.

        Args:
            embedding: The embedding vector to normalize.

        Returns:
            Normalized embedding vector with unit length.

        """
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm == 0:
            return embedding
        return [x / norm for x in embedding]

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
            config={"output_dimensionality": 1536},
        )
        if not result.embeddings:
            msg = f"Google embedding API returned no embeddings for model {self.model!r}"
            raise ValueError(msg)
        embedding = result.embeddings[0].values
        return self._normalize_embedding(embedding)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.

        """
        results = []
        for text in texts:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config={"output_dimensionality": 1536},
            )
            if not result.embeddings:
                msg = f"Google embedding API returned no embeddings for model {self.model!r}"
                raise ValueError(msg)
            embedding = result.embeddings[0].values
            results.append(self._normalize_embedding(embedding))
        return results

    def get_dimensions(self) -> int:
        """Get the dimension of embeddings produced by this embedder.

        Returns:
            Integer representing the embedding dimension.

        """
        return self._dimensions
