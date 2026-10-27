"""Factory function to get the configured embedder."""

import os

from django.conf import settings

from apps.ai.embeddings.base import Embedder


def get_embedder() -> Embedder:
    """Get the configured embedder.

    Returns:
        Embedder instance configured for the current provider.

    """
    provider = os.getenv("EMBEDDING_PROVIDER")
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if not provider:
        if llm_provider == "bedrock":
            msg = "EMBEDDING_PROVIDER is required when LLM_PROVIDER is bedrock"
            raise ValueError(msg)
        provider = llm_provider if llm_provider in {"openai", "google"} else "google"
    else:
        provider = provider.lower()

    if llm_provider == "bedrock":
        credential = {"openai": "OPEN_AI_SECRET_KEY", "google": "GOOGLE_API_KEY"}.get(provider)
        if credential and not getattr(settings, credential):
            msg = f"{credential} is required for the {provider} embedding provider"
            raise ValueError(msg)

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
