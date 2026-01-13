"""Factory function to get the configured embedder."""

from apps.ai.embeddings.base import Embedder
from apps.ai.embeddings.openai import OpenAIEmbedder


def get_embedder() -> Embedder:
    """Get the configured embedder.

    Currently returns OpenAI embedder, but can be extended to support
    other providers (e.g., Anthropic, Cohere, etc.).

    Returns:
        Embedder instance configured for the current provider.

    """
    # Currently OpenAI, but can be extended to support other providers
    return OpenAIEmbedder()
