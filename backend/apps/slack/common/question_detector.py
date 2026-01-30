"""Question detection utilities for Slack OWASP bot."""

from __future__ import annotations

import logging
import os

from django.core.exceptions import ObjectDoesNotExist
from pgvector.django.functions import CosineDistance

from apps.ai.common.llm_config import get_llm
from apps.ai.embeddings.factory import get_embedder
from apps.ai.models.chunk import Chunk
from apps.core.models.prompt import Prompt

logger = logging.getLogger(__name__)


class QuestionDetector:
    """Utility class for detecting OWASP-related questions."""

    MAX_TOKENS = 10
    TEMPERATURE = 0.1
    CHAT_MODEL = "gpt-4o-mini"
    CHUNKS_RETRIEVAL_LIMIT = 10

    def __init__(self) -> None:
        """Initialize the question detector."""
        self.llm = get_llm()
        self.embedder = get_embedder()

    def is_owasp_question(self, text: str) -> bool:
        """Check if the input text is an OWASP-related question.

        This is the main public method that orchestrates the detection logic.

        Args:
            text: The input text to check.
            context_chunks: Retrieved context chunks from the user's query.

        """
        if not text or not text.strip():
            return False

        context_chunks = self._retrieve_chunks(
            query=text,
            limit=self.CHUNKS_RETRIEVAL_LIMIT,
        )

        openai_result = self.is_owasp_question_with_llm(text, context_chunks)

        if openai_result is None:
            logger.warning(
                "OpenAI detection failed.",
            )
            return False

        return openai_result

    def is_owasp_question_with_llm(self, text: str, context_chunks: list[dict]) -> bool | None:
        """Determine if the text is an OWASP-related question using retrieved context chunks.

        Args:
            text: The question text to analyze.
            context_chunks: Retrieved context chunks from the user's query.

        Returns:
            - True: If the model responds with "YES".
            - False: If the model responds with "NO".
            - None: If the API call fails or the response is unexpected.

        """
        from crewai import Agent, Crew, Task

        prompt = Prompt.get_slack_question_detector_prompt()
        if not prompt or not prompt.strip():
            # Use a robust default if DB prompt is missing
            prompt = (
                "You are an expert OWASP assistant. Your task is to determine if a human question "
                "is related to OWASP, its projects, chapters, events, or general web security. "
                "Respond with 'YES' if it is related, and 'NO' otherwise. Be extremely concise.\n\n"
                "IMPORTANT: Simple greetings without questions (e.g., 'Hello', 'Hi', 'Thanks', 'Thank you') "
                "should be classified as 'NO' - they are not OWASP-related questions."
            )

        formatted_context = self.format_context_chunks(context_chunks)
        task_description = (
            f"{prompt}\n\n"
            f"CONTEXT CHUNKS:\n{formatted_context}\n\n"
            f"USER QUESTION: {text}\n\n"
            "Respond ONLY with 'YES' or 'NO'."
        )

        agent = Agent(
            role="OWASP Question Detector",
            goal="Identify if a question is related to OWASP or web security",
            backstory="You are a specialized filter for OWASP-related inquiries.",
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
        )

        task = Task(
            description=task_description,
            agent=agent,
            expected_output="'YES' or 'NO'",
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
        )

        try:
            result = str(crew.kickoff()).strip().upper()
            if "YES" in result:
                return True
            if "NO" in result:
                return False
            logger.warning(
                "Question Detector: Unexpected result format",
                extra={"result": result},
            )
            return None
        except Exception:
            logger.exception("Agent-based detection failed")
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

    def _retrieve_chunks(self, query: str, limit: int) -> list[dict]:
        """Retrieve context chunks using semantic search.

        Args:
            query: The search query
            limit: Maximum number of results to return

        Returns:
            List of dictionaries with chunk information

        """
        query_embedding = self.embedder.embed_query(query)

        chunks = Chunk.objects.annotate(
            distance=CosineDistance("embedding", query_embedding)
        ).order_by("distance")[:limit]

        return [
            {
                "text": chunk.text,
                "source_name": str(chunk.context) if chunk.context else "Unknown",
                "additional_context": {},
            }
            for chunk in chunks
        ]
