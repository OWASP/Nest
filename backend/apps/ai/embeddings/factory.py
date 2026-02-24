"""Factory function to get the configured embedder."""

import os

from apps.ai.embeddings.base import Embedder
from apps.ai.embeddings.google import GoogleEmbedder
from apps.ai.embeddings.openai import OpenAIEmbedder


def get_embedder() -> Embedder:
    """Get the configured embedder.

    Currently returns OpenAI and Google embedder, but can be extended to support
    other providers (e.g., Anthropic, Cohere, etc.).

    Returns:
        Embedder instance configured for the current provider.

    """
    if os.getenv("LLM_PROVIDER", "openai") == "google":
        return GoogleEmbedder()

    return OpenAIEmbedder()
