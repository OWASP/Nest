"""Factory function to get the configured embedder."""

import os

from apps.ai.embeddings.base import Embedder
from apps.ai.embeddings.google import GoogleEmbedder
from apps.ai.embeddings.openai import OpenAIEmbedder


def get_embedder() -> Embedder:
    """Get the configured embedder.

    Returns:
        Embedder instance configured for the current provider.

    """
    provider = os.getenv("LLM_PROVIDER", "openai")

    if provider == "openai":
        return OpenAIEmbedder()

    if provider == "google":
        return GoogleEmbedder()

    error_msg = f"Unsupported LLM provider: {provider}"

    raise ValueError(error_msg)
