"""Factory function to get the configured embedder."""

import os

from apps.ai.embeddings.base import Embedder


def get_embedder() -> Embedder:
    """Get the configured embedder.

    Returns:
        Embedder instance configured for the current provider.

    """
    provider = os.getenv("EMBEDDING_PROVIDER")
    if not provider:
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        provider = llm_provider if llm_provider in {"openai", "google"} else "google"
    else:
        provider = provider.lower()

    match provider:
        case "openai":
            from apps.ai.embeddings.openai import OpenAIEmbedder  # noqa: PLC0415

            return OpenAIEmbedder()
        case "google":
            from apps.ai.embeddings.google import GoogleEmbedder  # noqa: PLC0415

            return GoogleEmbedder()
        case _:
            error_msg = f"Unsupported embedding provider: {provider}"
            raise ValueError(error_msg)
