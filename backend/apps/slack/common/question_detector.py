"""Question detection utilities for Slack OWASP bot."""

from __future__ import annotations

import logging
import os

import openai
from django.core.exceptions import ObjectDoesNotExist

from apps.ai.agent.tools.rag.retriever import Retriever
from apps.ai.common.constants import (
    DEFAULT_SIMILARITY_THRESHOLD,
)
from apps.core.models.prompt import Prompt

logger = logging.getLogger(__name__)


class QuestionDetector:
    """Utility class for detecting OWASP-related questions."""

    MAX_TOKENS = 10
    TEMPERATURE = 0.1
    CHAT_MODEL = "gpt-4o-mini"
    CHUNKS_RETRIEVAL_LIMIT = 10

    def __init__(self):
        """Initialize the question detector.

        Raises:
            ValueError: If the OpenAI API key is not set.

        """
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            error_msg = "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            raise ValueError(error_msg)

        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.retriever = Retriever()

    def is_owasp_question(self, text: str) -> bool:
        """Check if the input text is an OWASP-related question.

        This is the main public method that orchestrates the detection logic.

        Args:
            text: The input text to check.
            context_chunks: Retrieved context chunks from the user's query.

        """
        if not text or not text.strip():
            return False

        context_chunks: list[dict] = []
        if not context_chunks:
            context_chunks = self.retriever.retrieve(
                query=text,
                limit=self.CHUNKS_RETRIEVAL_LIMIT,
                similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD,
            )

        openai_result = self.is_owasp_question_with_openai(text, context_chunks)

        if openai_result is None:
            logger.warning(
                "OpenAI detection failed.",
            )
            return False

        return openai_result

    def is_owasp_question_with_openai(
        self, text: str, context_chunks: list[dict] | None = None
    ) -> bool | None:
        """Determine if the text is an OWASP-related question using retrieved context chunks.

        Args:
            text: The question text to analyze.
            context_chunks: Retrieved context chunks from the user's query.

        Returns:
            - True: If the model responds with "YES".
            - False: If the model responds with "NO".
            - None: If the API call fails or the response is unexpected.

        """
        prompt = Prompt.get_slack_question_detector_prompt()

        if not prompt or not prompt.strip():
            error_msg = "Prompt with key 'slack-question-detector-system-prompt' not found."
            raise ObjectDoesNotExist(error_msg)

        formatted_context = (
            self.format_context_chunks(context_chunks)
            if context_chunks
            else "No context available"
        )
        system_prompt = prompt
        user_prompt = f'Question: "{text}"\n\n Context: {formatted_context}'

        try:
            response = self.openai_client.chat.completions.create(
                model=self.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )
        except openai.OpenAIError:
            logger.exception("OpenAI API error during question detection")
            return None
        else:
            answer = response.choices[0].message.content
            if not answer:
                logger.error("OpenAI returned an empty response")
                return None

            clean_answer = answer.strip().upper()

            if "YES" in clean_answer:
                return True
            if "NO" in clean_answer:
                return False
            logger.warning("Unexpected OpenAI response")
            return None

    def format_context_chunks(self, context_chunks: list[dict]) -> str:
        """Format the list of retrieved context chunks into a single string for analysis.

        Args:
            context_chunks: A list of chunk dictionaries from the retriever.

        Returns:
            A formatted string containing the context.

        """
        if not context_chunks:
            return "No context provided"

        formatted_context = []
        for i, chunk in enumerate(context_chunks):
            source_name = chunk.get("source_name", f"Unknown Source {i + 1}")
            text = chunk.get("text", "")
            additional_context = chunk.get("additional_context", {})

            if additional_context:
                context_block = (
                    f"Source Name: {source_name}\nContent: {text}\n"
                    f"Additional Context: {additional_context}"
                )
            else:
                context_block = f"Source Name: {source_name}\nContent: {text}"

            formatted_context.append(context_block)

        return "\n\n---\n\n".join(formatted_context)
