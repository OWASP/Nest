"""LLM configuration for CrewAI agents."""

from __future__ import annotations

from crewai import LLM
from django.conf import settings


def get_llm() -> LLM:
    """Get configured LLM instance.

    Returns:
        LLM: Configured LLM instance based on settings.

    """
    provider = settings.LLM_PROVIDER

    if provider == "openai":
        return LLM(
            model=settings.OPENAI_MODEL_NAME,
            api_key=settings.OPEN_AI_SECRET_KEY,
            temperature=0.1,
        )
    if provider == "google":
        return LLM(
            model=f"openai/{settings.GOOGLE_MODEL_NAME}",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.1,
        )

    # Fallback to OpenAI if provider not recognized or not specified
    return LLM(
        model=settings.OPENAI_MODEL_NAME,
        api_key=settings.OPEN_AI_SECRET_KEY,
        temperature=0.1,
    )
