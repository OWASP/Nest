"""Generator for the RAG system."""

import logging
import os
from typing import Any

import openai
from django.core.exceptions import ObjectDoesNotExist

from apps.core.models.prompt import Prompt

logger = logging.getLogger(__name__)


class Generator:
    """Generates answers to user queries based on retrieved context."""

    MAX_TOKENS = 2000
    TEMPERATURE = 0.8

    def __init__(self, chat_model: str = "gpt-4o"):
        """Initialize the Generator.

        Args:
          chat_model (str): The name of the OpenAI chat model to use for generation.

        Raises:
          ValueError: If the OpenAI API key is not set.

        """
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            error_msg = "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            raise ValueError(error_msg)

        self.chat_model = chat_model
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        logger.info("Generator initialized with chat model: %s", self.chat_model)

    def prepare_context(self, context_chunks: list[dict[str, Any]]) -> str:
        """Format the list of retrieved context chunks into a single string for the LLM.

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

            context_block = f"Source Name: {source_name}\nContent: {text}"
            formatted_context.append(context_block)

        return "\n\n---\n\n".join(formatted_context)

    def generate_answer(self, query: str, context_chunks: list[dict[str, Any]]) -> str:
        """Generate an answer to the user's query using provided context chunks.

        Args:
          query: The user's query text.
          context_chunks: A list of context chunks retrieved by the retriever.

        Returns:
          The generated answer as a string.

        """
        formatted_context = self.prepare_context(context_chunks)

        user_prompt = f"""
Question: {query}
Context: {formatted_context}
Answer:
"""

        try:
            system_prompt = Prompt.get_rag_system_prompt()
            if not system_prompt or not system_prompt.strip():
                error_msg = "Prompt with key 'rag-system-prompt' not found."
                raise ObjectDoesNotExist(error_msg)

            response = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )
            answer = response.choices[0].message.content.strip()
        except openai.OpenAIError:
            logger.exception("OpenAI API error")
            answer = "I'm sorry, I'm currently unable to process your request."

        return answer
