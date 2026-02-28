"""LLM configuration for CrewAI agents."""

from __future__ import annotations

import logging
import os

from crewai import LLM
from django.conf import settings

logger = logging.getLogger(__name__)


def get_llm() -> LLM:
    """Get configured LLM instance.

    Returns:
        LLM: Configured LLM instance with gpt-4.1-mini as default model.

    """
    provider = os.getenv("LLM_PROVIDER", "openai")

    if provider == "openai":
        return LLM(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini"),
            api_key=settings.OPEN_AI_SECRET_KEY,
            temperature=0.1,
        )

    if provider == "google":
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")
        if not model_name.startswith("gemini/"):
            model_name = f"gemini/{model_name}"
        return LLM(
            model=model_name,
            api_key=settings.GOOGLE_API_KEY,
            temperature=0.1,
        )

    error_msg = f"Unsupported LLM provider: {provider}"

    raise ValueError(error_msg)
