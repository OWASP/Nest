"""Factory function to get the configured embedder."""

from django.conf import settings

from apps.ai.embeddings.base import Embedder
from apps.ai.embeddings.google import GoogleEmbedder
from apps.ai.embeddings.openai import OpenAIEmbedder


def get_embedder() -> Embedder:
    """Get the configured embedder.

    Currently returns OpenAI and gemini embedder, but can be extended to support
    other providers (e.g., Anthropic, Cohere, etc.).

    Returns:
        Embedder instance configured for the current provider.

    """
    # Currently OpenAI and gemini, but can be extended to support other providers
    if settings.LLM_PROVIDER == "google":
        return GoogleEmbedder()

    return OpenAIEmbedder()
