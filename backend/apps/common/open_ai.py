"""Open AI API module."""

from __future__ import annotations

import base64
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
        self.image_data: bytes | None = None
        self.image_mime_type: str | None = None

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

    def set_image(self, image_data: bytes, mime_type: str) -> OpenAi:
        """Set image data for vision API.

        Args:
            image_data (bytes): Raw image bytes.
            mime_type (str): MIME type of the image (e.g., "image/png").

        Returns:
            OpenAi: The current instance.

        """
        self.image_data = image_data
        self.image_mime_type = mime_type

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
            # Build user message content
            user_content: str | list[dict[str, object]]
            if self.image_data and self.image_mime_type:
                # Vision API with image
                base64_image = base64.b64encode(self.image_data).decode("utf-8")
                user_content = [
                    {"type": "text", "text": self.input},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{self.image_mime_type};base64,{base64_image}"},
                    },
                ]
            else:
                # Text-only
                user_content = self.input

            response = self.client.chat.completions.create(
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": user_content},
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
