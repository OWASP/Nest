"""Google implementation of embedder."""

from __future__ import annotations

import requests
from django.conf import settings

from apps.ai.embeddings.base import Embedder


class GoogleEmbedder(Embedder):
    """Google implementation of embedder using OpenAI compatible endpoint."""

    def __init__(self, model: str = "text-embedding-004") -> None:
        """Initialize Google embedder.

        Args:
            model: The Google embedding model to use.

        """
        self.api_key = settings.GOOGLE_API_KEY
        self.model = model
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/openai/embeddings"
        self._dimensions = 768  # text-embedding-004 dimensions

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query string.

        Args:
            text: The query text to embed.

        Returns:
            List of floats representing the embedding vector.

        """
        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "input": text,
                "model": self.model,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.

        """
        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "input": texts,
                "model": self.model,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    def get_dimensions(self) -> int:
        """Get the dimension of embeddings produced by this embedder.

        Returns:
            Integer representing the embedding dimension.

        """
        return self._dimensions
