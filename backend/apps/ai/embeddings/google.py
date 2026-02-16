"""Google implementation of embedder."""

from __future__ import annotations

try:
    from google import genai
except ImportError:
    # Fallback to deprecated package if new one not available
    try:
        import warnings

        import google.generativeai as genai

        warnings.warn(
            (
                "google.generativeai is deprecated. "
                "Please install google-genai package: pip install google-genai"
            ),
            DeprecationWarning,
            stacklevel=2,
        )
    except ImportError:
        genai = None

import requests
from django.conf import settings

from apps.ai.embeddings.base import Embedder


class GoogleEmbedder(Embedder):
    """Google implementation of embedder using Google Generative AI SDK."""

    def __init__(self, model: str = "gemini-embedding-001") -> None:
        """Initialize Google embedder.

        Args:
            model: The Google embedding model to use.
                  Default: gemini-embedding-001 (recommended, 768 dimensions)
                  Note: text-embedding-004 is deprecated

        """
        self.api_key = settings.GOOGLE_API_KEY
        self.model = model
        # gemini-embedding-001 has 768 dimensions
        self._dimensions = 768

        # Use Google Generative AI SDK (preferred method)
        # The SDK handles endpoint URLs and authentication automatically
        if genai:
            genai.configure(api_key=self.api_key)
            self.use_sdk = True
        else:
            # Fallback to REST API (not recommended - use SDK instead)
            self.base_url = "https://generativelanguage.googleapis.com/v1beta"
            self.use_sdk = False
            import warnings

            warnings.warn(
                "Google GenAI SDK not available. Install it with: pip install google-genai",
                UserWarning,
                stacklevel=2,
            )

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query string.

        Args:
            text: The query text to embed.

        Returns:
            List of floats representing the embedding vector.

        """
        if self.use_sdk and genai:
            # Use Google Generative AI SDK (preferred method)
            # SDK automatically handles the correct endpoint and model format
            result = genai.embed_content(
                model=self.model,
                content=text,
            )
            # SDK returns embedding in 'embedding' key
            return result["embedding"]

        # Fallback to REST API
        endpoint = f"{self.base_url}/models/{self.model}:embedContent?key={self.api_key}"
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json={
                "content": {"parts": [{"text": text}]},
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]["values"]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple documents.

        Args:
            texts: List of document texts to embed.

        Returns:
            List of embedding vectors, one per document.

        """
        if self.use_sdk and genai:
            # Use Google Generative AI SDK (preferred method)
            # SDK handles batching automatically
            results = []
            for text in texts:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                )
                results.append(result["embedding"])
            return results

        # Fallback to REST API
        endpoint = f"{self.base_url}/models/{self.model}:batchEmbedContents?key={self.api_key}"
        response = requests.post(
            endpoint,
            headers={"Content-Type": "application/json"},
            json={
                "requests": [{"content": {"parts": [{"text": text}]}} for text in texts],
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"]["values"] for item in data["embeddings"]]

    def get_dimensions(self) -> int:
        """Get the dimension of embeddings produced by this embedder.

        Returns:
            Integer representing the embedding dimension.

        """
        return self._dimensions
