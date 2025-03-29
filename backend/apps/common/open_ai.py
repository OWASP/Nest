"""Open AI API module."""

import logging

import openai
from django.conf import settings

logger = logging.getLogger(__name__)


class OpenAi:
    """Open AI communication class."""

    def __init__(self, model="gpt-4o-mini", max_tokens=1000, temperature=0.7):
        """OpenAi constructor.

        Args:
        ----
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

    def set_input(self, content):
        """Set system role content.

        Args:
        ----
            content (str): The input content.

        Returns:
        -------
            OpenAi: The current instance.

        """
        self.input = content

        return self

    def set_max_tokens(self, max_tokens):
        """Set max tokens.

        Args:
        ----
            max_tokens (int): Maximum tokens for the response.

        Returns:
        -------
            OpenAi: The current instance.

        """
        self.max_tokens = max_tokens

        return self

    def set_prompt(self, content):
        """Set system role content.

        Args:
        ----
            content (str): The prompt content.

        Returns:
        -------
            OpenAi: The current instance.

        """
        self.prompt = content

        return self

    def complete(self):
        """Get API response.

        Returns
        -------
            str: The response content.

        Raises
        ------
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
        except openai.APIConnectionError:
            logger.exception("A connection error occurred during OpenAI API request.")
        except Exception:
            logger.exception("An error occurred during OpenAI API request.")
