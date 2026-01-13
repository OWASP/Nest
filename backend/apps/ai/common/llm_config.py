"""LLM configuration for CrewAI agents."""

from __future__ import annotations

import os

from crewai import LLM


def get_llm() -> LLM:
    """Get configured LLM instance.

    Returns:
        LLM: Configured LLM instance with gpt-4.1-mini as default model.

    """
    provider = os.getenv("LLM_PROVIDER", "openai")

    if provider == "openai":
        return LLM(
            model=os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini"),
            api_key=os.getenv("DJANGO_OPEN_AI_SECRET_KEY"),
            temperature=0.1,
        )
    if provider == "anthropic":
        return LLM(
            model=os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet-20241022"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.1,
        )

    error_msg = f"Unsupported LLM provider: {provider}"
    raise ValueError(error_msg)
