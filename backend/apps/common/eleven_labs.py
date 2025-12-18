"""ElevenLabs API module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from elevenlabs.client import ElevenLabs as ElevenLabsClient

if TYPE_CHECKING:
    from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


class ElevenLabs:
    """ElevenLabs communication class."""

    def __init__(
        self,
        voice_id: str = "Xb7hH8MSUJpSbSDYk0k2",  # cspell:disable-line
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
    ) -> None:
        """ElevenLabs constructor.

        Args:
            voice_id (str, optional): The voice ID to use.
            model_id (str, optional): The model to use.
            output_format (str, optional): Audio output format.

        """
        self.client = ElevenLabsClient(
            api_key=settings.ELEVENLABS_API_KEY,
            timeout=30,
        )

        self.model_id = model_id
        self.output_format = output_format
        self.voice_id = voice_id

    def set_text(self, text: str) -> ElevenLabs:
        """Set the text to convert to speech.

        Args:
            text (str): The text content.

        Returns:
            ElevenLabs: The current instance.

        """
        self.text = text

        return self

    def set_voice_id(self, voice_id: str) -> ElevenLabs:
        """Set voice ID.

        Args:
            voice_id (str): The voice ID.

        Returns:
            ElevenLabs: The current instance.

        """
        self.voice_id = voice_id

        return self

    def set_model_id(self, model_id: str) -> ElevenLabs:
        """Set model ID.

        Args:
            model_id (str): The model ID.

        Returns:
            ElevenLabs: The current instance.

        """
        self.model_id = model_id

        return self

    def set_output_format(self, output_format: str) -> ElevenLabs:
        """Set output format.

        Args:
            output_format (str): The audio output format.

        Returns:
            ElevenLabs: The current instance.

        """
        self.output_format = output_format

        return self

    def generate(self) -> bytes | None:
        """Generate audio from text.

        Returns:
            bytes | None: The audio bytes or None on error.

        """
        try:
            audio_iterator = self.client.text_to_speech.convert(
                text=self.text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                output_format=self.output_format,
            )

            return b"".join(audio_iterator)
        except Exception:
            logger.exception("An error occurred during ElevenLabs API request.")

        return None

    def generate_to_file(self, file_path: Path) -> bool:
        """Generate audio and save to file.

        Args:
            file_path (Path): Path to save the audio file.

        Returns:
            bool: True if successful, False otherwise.

        """
        audio = self.generate()
        if audio is None:
            return False

        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(audio)

        return True
