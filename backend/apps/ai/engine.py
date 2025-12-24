"""LLM Engine for generating responses from sanitized project data.

Security: Accepts only ProjectPublicDTO objects, never raw database models
or arbitrary dictionaries. This prevents prompt injection via unsanitized
fields (OWASP LLM01).
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import openai

if TYPE_CHECKING:
    from apps.core.services.project_service import ProjectPublicDTO

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful assistant for OWASP projects. "
    "Answer questions using the provided project information. "
    "Be concise and direct. If you don't have enough information, say so."
)

FALLBACK_RESPONSE = (
    "I found the following resources but could not generate a summary. "
    "Please check the links above."
)


class Engine:
    """Generates natural language answers from structured project data."""

    MAX_TOKENS = 800
    TEMPERATURE = 0

    def __init__(self, chat_model: str = "gpt-4o") -> None:
        """Initialize the Engine.

        Args:
            chat_model: The OpenAI chat model to use for generation.

        Raises:
            ValueError: If the API key environment variable is missing.

        """
        api_key = os.getenv("DJANGO_OPEN_AI_SECRET_KEY")
        if not api_key:
            msg = "DJANGO_OPEN_AI_SECRET_KEY not set"
            raise ValueError(msg)

        self.chat_model = chat_model
        self.openai_client = openai.OpenAI(api_key=api_key)
        logger.info("Engine initialized with chat model: %s", self.chat_model)

    def _format_context(self, projects: list[ProjectPublicDTO]) -> str:
        """Build a text block from project DTOs for LLM context.

        Args:
            projects: Sanitized project data.

        Returns:
            Formatted multi-line string.

        """
        if not projects:
            return "No matching projects found."

        blocks = []
        for p in projects:
            lines = [f"Project: {p.name}"]
            if p.url:
                lines.append(f"URL: {p.url}")
            if p.description:
                lines.append(f"Description: {p.description}")
            if p.maintainers:
                lines.append(f"Maintainers: {', '.join(p.maintainers)}")
            blocks.append("\n".join(lines))

        return "\n---\n".join(blocks)

    def generate_answer(self, query: str, projects: list[ProjectPublicDTO]) -> str:
        """Generate a response using the LLM.

        Args:
            query: User's question.
            projects: Sanitized project DTOs to use as context.

        Returns:
            Generated answer, or a fallback message if the API fails.

        """
        context = self._format_context(projects)
        user_msg = f"Question: {query}\n\nProjects:\n{context}"

        try:
            resp = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )
            # Defensive check for empty choices or content
            if resp.choices and resp.choices[0].message.content:
                return resp.choices[0].message.content.strip()
            return FALLBACK_RESPONSE

        except openai.OpenAIError:
            logger.exception("LLM API call failed")
            return FALLBACK_RESPONSE
