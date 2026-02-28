"""Open AI API module."""

from __future__ import annotations

import logging

import openai
from django.conf import settings

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

        self.max_tokens = max_tokens
        self.model = model
        self.temperature = temperature

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
                    {"role": "user", "content": self.input},
                ],
                model=self.model,
                temperature=self.temperature,
            )

            return response.choices[0].message.content
        except openai.AuthenticationError:
            # environment variable name used by the project is OPEN_AI_SECRET_KEY,
            # the earlier log referenced DJANGO_OPEN_AI_SECRET_KEY which is
            # inaccurate and could mislead operators troubleshooting auth errors.
            logger.exception("OpenAI authentication error - check OPEN_AI_SECRET_KEY")
        except openai.RateLimitError:
            logger.exception("OpenAI rate limit exceeded - request may be retried")
        except openai.BadRequestError:
            logger.exception("Invalid OpenAI request - check model/message format")
        except openai.APIConnectionError:
            logger.exception("A connection error occurred during OpenAI API request.")
        except Exception as e:
            logger.exception(
                "Unexpected error during OpenAI API request: %s",
                type(e).__name__,
            )
        return None
