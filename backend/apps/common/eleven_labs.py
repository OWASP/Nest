"""ElevenLabs API module."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from elevenlabs.client import ElevenLabs as ElevenLabsClient
from elevenlabs.types.voice_settings import VoiceSettings

if TYPE_CHECKING:
    from pathlib import Path

logger: logging.Logger = logging.getLogger(__name__)


class ElevenLabs:
    """ElevenLabs communication class."""

    def __init__(
        self,
        model_id: str = "eleven_multilingual_v2",
        output_format: str = "mp3_44100_128",
        similarity_boost: float = 0.75,
        speed: float = 1.0,
        stability: float = 0.5,
        style: float = 0.0,
        voice_id: str = "1SM7GgM6IMuvQlz2BwM3",  # cspell:disable-line
        *,
        use_speaker_boost: bool = True,
    ) -> None:
        """ElevenLabs constructor.

        Args:
            model_id (str): The model to use.
            output_format (str): Audio output format.
            similarity_boost (float): Voice consistency (0.0-1.0).
            speed (float): Speech speed (0.25-4.0, default 1.0).
            stability (float): Voice stability (0.0-1.0).
            style (float): Style exaggeration (0.0-1.0).
            use_speaker_boost (bool): Enable speaker clarity boost.
            voice_id (str): The voice ID to use.

        Raises:
            ValueError: If the ElevenLabs API key is not set.

        """
        if not (api_key := os.getenv("DJANGO_ELEVENLABS_API_KEY")):
            error_msg = "DJANGO_ELEVENLABS_API_KEY environment variable not set"
            raise ValueError(error_msg)

        self.client = ElevenLabsClient(
            api_key=api_key,
            timeout=30,
        )

        self.model_id = model_id
        self.output_format = output_format
        self.similarity_boost = similarity_boost
        self.speed = speed
        self.stability = stability
        self.style = style
        self.use_speaker_boost = use_speaker_boost
        self.voice_id = voice_id

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

    def set_similarity_boost(self, similarity_boost: float) -> ElevenLabs:
        """Set similarity boost.

        Args:
            similarity_boost (float): Voice consistency (0.0-1.0).

        Returns:
            ElevenLabs: The current instance.

        """
        self.similarity_boost = similarity_boost

        return self

    def set_speed(self, speed: float) -> ElevenLabs:
        """Set speech speed.

        Args:
            speed (float): Speech speed (0.25-4.0, default 1.0).

        Returns:
            ElevenLabs: The current instance.

        """
        self.speed = speed

        return self

    def set_stability(self, stability: float) -> ElevenLabs:
        """Set stability.

        Args:
            stability (float): Voice stability (0.0-1.0).

        Returns:
            ElevenLabs: The current instance.

        """
        self.stability = stability

        return self

    def set_style(self, style: float) -> ElevenLabs:
        """Set style exaggeration.

        Args:
            style (float): Style exaggeration (0.0-1.0).

        Returns:
            ElevenLabs: The current instance.

        """
        self.style = style

        return self

    def set_text(self, text: str) -> ElevenLabs:
        """Set the text to convert to speech.

        Args:
            text (str): The text content.

        Returns:
            ElevenLabs: The current instance.

        """
        self.text = text

        return self

    def set_use_speaker_boost(self, *, use_speaker_boost: bool) -> ElevenLabs:
        """Set speaker boost.

        Args:
            use_speaker_boost (bool): Enable speaker clarity boost.

        Returns:
            ElevenLabs: The current instance.

        """
        self.use_speaker_boost = use_speaker_boost

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

    def generate(self) -> bytes:
        """Generate audio from text.

        Returns:
            bytes: The audio bytes.

        """
        audio_iterator = self.client.text_to_speech.convert(
            model_id=self.model_id,
            output_format=self.output_format,
            text=self.text,
            voice_id=self.voice_id,
            voice_settings=VoiceSettings(
                similarity_boost=self.similarity_boost,
                speed=self.speed,
                stability=self.stability,
                style=self.style,
                use_speaker_boost=self.use_speaker_boost,
            ),
        )

        return b"".join(audio_iterator)

    def save(self, contents: bytes, file_path: Path) -> None:
        """Save audio contents to file.

        Args:
            contents (bytes): The audio content to save.
            file_path (Path): Path to save the audio file.

        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(contents)
