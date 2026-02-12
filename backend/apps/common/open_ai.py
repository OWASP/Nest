"""Open AI API module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import openai
from django.conf import settings
from openai.types.chat import ChatCompletionContentPartParam

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionContentPartParam

logger: logging.Logger = logging.getLogger(__name__)


class OpenAi:
    """Open AI communication class."""

    def __init__(
        self, model: str = "gpt-4o-mini", max_tokens: int = 1000, temperature: float = 0.7
    ) -> None:
        """OpenAi constructor.

        Args:
            model (str, optional): The model to use.
            max_tokens (int, optional): Maximum tokens for the response.
            temperature (float, optional): Sampling temperature.

        """
        self.client = openai.OpenAI(
            api_key=settings.OPEN_AI_SECRET_KEY,
            timeout=30,  # In seconds.
        )

        self.images: list[str] = []
        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temperature

    def set_images(self, images: list[str]) -> OpenAi:
        """Set images data URI.

        Args:
            images (list[str]): A list of base64 encoded image data URIs.

        Returns:
            OpenAi: The current instance.

        """
        self.images = images

        return self

    def set_input(self, content: str) -> OpenAi:
        """Set system role content.

        Args:
            content (str): The input content.

        Returns:
            OpenAi: The current instance.

        """
        self.input = content

        return self

    def set_max_tokens(self, max_tokens: int) -> OpenAi:
        """Set max tokens.

        Args:
            max_tokens (int): Maximum tokens for the response.

        Returns:
            OpenAi: The current instance.

        """
        self.max_tokens = max_tokens

        return self

    def set_prompt(self, content: str) -> OpenAi:
        """Set system role content.

        Args:
            content (str): The prompt content.

        Returns:
            OpenAi: The current instance.

        """
        self.prompt = content

        return self

    @property
    def user_content(self) -> list[ChatCompletionContentPartParam]:
        """User message content.

        Returns:
            list[dict]: User message content.

        """
        content: list[ChatCompletionContentPartParam] = [{"type": "text", "text": self.input}]
        content.extend({"type": "image_url", "image_url": {"url": uri}} for uri in self.images)
        return content

    def complete(self) -> str | None:
        """Get API response.

        Returns
            str: The response content.

        Raises
            openai.APIConnectionError: If a connection error occurs.
            Exception: For other errors during the API request.

        """
        try:
            response = self.client.chat.completions.create(
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.user_content},
                ],
                model=self.model,
                temperature=self.temperature,
            )

            return response.choices[0].message.content
        except openai.APIConnectionError:
            logger.exception("A connection error occurred during OpenAI API request.")
        except Exception:
            logger.exception("An error occurred during OpenAI API request.")
        return None
