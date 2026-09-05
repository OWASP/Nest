"""Open AI API module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypeVar

import openai
from django.conf import settings

if TYPE_CHECKING:
    from pydantic import BaseModel

logger: logging.Logger = logging.getLogger(__name__)

T = TypeVar("T", bound="BaseModel")


class OpenAi:
    """Open AI communication class."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: int = 30,
    ) -> None:
        """OpenAi constructor.

        Args:
            model (str, optional): The model to use.
            max_tokens (int, optional): Maximum tokens for the response.
            temperature (float, optional): Sampling temperature.
            timeout (int, optional): Request timeout in seconds. Defaults to 30.

        """
        self.client = openai.OpenAI(
            api_key=settings.OPEN_AI_SECRET_KEY,
            timeout=timeout,
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

    def parse(self, schema: type[T]) -> T | None:
        """Get a structured response validated against a pydantic schema.

        Args:
            schema (type[T]): A pydantic model class.

        Returns:
            T | None: A validated instance of the schema, or None on error.

        """
        try:
            response = self.client.beta.chat.completions.parse(
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": self.input},
                ],
                model=self.model,
                response_format=schema,
                temperature=self.temperature,
            )
            return response.choices[0].message.parsed
        except openai.AuthenticationError:
            logger.exception("OpenAI authentication failed: invalid or missing API key. ")
        except openai.RateLimitError as e:
            logger.warning(
                "OpenAI rate limit exceeded: %s. Request may be retried with backoff.",
                e,
            )
        except openai.BadRequestError:
            logger.exception(
                "OpenAI invalid request. Check model name, message format, and input size."
            )
        except openai.APIConnectionError:
            logger.exception(
                "OpenAI connection failed. Check network connectivity and firewall/proxy settings."
            )
        except Exception as e:
            logger.exception(
                "Unexpected OpenAI API error: %s",
                type(e).__name__,
            )
        return None

    def complete(self) -> str | None:
        """Get API response.

        Returns
            str: The response content.

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
            logger.exception(
                "OpenAI authentication failed: invalid or missing API key. "
                "Verify DJANGO_OPEN_AI_SECRET_KEY is set and valid."
            )
        except openai.RateLimitError as e:
            logger.warning(
                "OpenAI rate limit exceeded: %s. Request may be retried with backoff.",
                e,
            )
        except openai.BadRequestError:
            logger.exception(
                "OpenAI invalid request. Check model name, message format, and input size."
            )
        except openai.APIConnectionError:
            logger.exception(
                "OpenAI connection failed. Check network connectivity and firewall/proxy settings."
            )
        except Exception as e:
            logger.exception(
                "Unexpected OpenAI API error: %s",
                type(e).__name__,
            )
        return None
