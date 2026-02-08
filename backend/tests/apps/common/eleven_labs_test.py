from unittest.mock import patch

import pytest

from apps.common.eleven_labs import ElevenLabs

DEFAULT_API_KEY = "test_api_key"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_SIMILARITY_BOOST = 0.75
DEFAULT_SPEED = 0.75
DEFAULT_STABILITY = 0.5
DEFAULT_STYLE = 0.0
DEFAULT_TIMEOUT = 30
DEFAULT_USE_SPEAKER_BOOST = True
DEFAULT_VOICE_ID = "TX3LPaxmHKxFdv7VOQHJ"  # cspell:disable-line


class TestElevenLabs:
    @pytest.fixture
    def elevenlabs_instance(self):
        with (
            patch.dict("os.environ", {"DJANGO_ELEVENLABS_API_KEY": DEFAULT_API_KEY}),
            patch("apps.common.eleven_labs.ElevenLabsClient"),
        ):
            return ElevenLabs()

    @patch("apps.common.eleven_labs.ElevenLabsClient")
    def test_init(self, mock_client):
        with patch.dict("os.environ", {"DJANGO_ELEVENLABS_API_KEY": DEFAULT_API_KEY}):
            instance = ElevenLabs()

        mock_client.assert_called_once_with(api_key=DEFAULT_API_KEY, timeout=DEFAULT_TIMEOUT)
        assert instance.model_id == DEFAULT_MODEL_ID
        assert instance.output_format == DEFAULT_OUTPUT_FORMAT
        assert instance.similarity_boost == DEFAULT_SIMILARITY_BOOST
        assert instance.speed == DEFAULT_SPEED
        assert instance.stability == DEFAULT_STABILITY
        assert instance.style == DEFAULT_STYLE
        assert instance.use_speaker_boost == DEFAULT_USE_SPEAKER_BOOST
        assert instance.voice_id == DEFAULT_VOICE_ID

    def test_init_raises_without_api_key(self):
        """Test init raises ValueError when API key not set."""
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="DJANGO_ELEVENLABS_API_KEY"),
        ):
            ElevenLabs()

    @pytest.mark.parametrize(
        ("model_id", "expected_model_id"),
        [("eleven_monolingual_v1", "eleven_monolingual_v1")],
    )
    def test_set_model_id(self, elevenlabs_instance, model_id, expected_model_id):
        result = elevenlabs_instance.set_model_id(model_id)
        assert result.model_id == expected_model_id

    @pytest.mark.parametrize(
        ("output_format", "expected_output_format"),
        [("mp3_22050_32", "mp3_22050_32")],
    )
    def test_set_output_format(self, elevenlabs_instance, output_format, expected_output_format):
        result = elevenlabs_instance.set_output_format(output_format)
        assert result.output_format == expected_output_format

    @pytest.mark.parametrize(
        ("similarity_boost", "expected_similarity_boost"),
        [(0.9, 0.9)],
    )
    def test_set_similarity_boost(
        self, elevenlabs_instance, similarity_boost, expected_similarity_boost
    ):
        result = elevenlabs_instance.set_similarity_boost(similarity_boost)
        assert result.similarity_boost == expected_similarity_boost

    @pytest.mark.parametrize(
        ("speed", "expected_speed"),
        [(0.85, 0.85)],
    )
    def test_set_speed(self, elevenlabs_instance, speed, expected_speed):
        result = elevenlabs_instance.set_speed(speed)
        assert result.speed == expected_speed

    @pytest.mark.parametrize(
        ("stability", "expected_stability"),
        [(0.8, 0.8)],
    )
    def test_set_stability(self, elevenlabs_instance, stability, expected_stability):
        result = elevenlabs_instance.set_stability(stability)
        assert result.stability == expected_stability

    @pytest.mark.parametrize(
        ("style", "expected_style"),
        [(0.5, 0.5)],
    )
    def test_set_style(self, elevenlabs_instance, style, expected_style):
        result = elevenlabs_instance.set_style(style)
        assert result.style == expected_style

    @pytest.mark.parametrize(
        ("text", "expected_text"),
        [("Hello, world!", "Hello, world!")],
    )
    def test_set_text(self, elevenlabs_instance, text, expected_text):
        result = elevenlabs_instance.set_text(text)
        assert result.text == expected_text

    @pytest.mark.parametrize(
        ("use_speaker_boost", "expected_use_speaker_boost"),
        [(False, False)],
    )
    def test_set_use_speaker_boost(
        self, elevenlabs_instance, use_speaker_boost, expected_use_speaker_boost
    ):
        result = elevenlabs_instance.set_use_speaker_boost(use_speaker_boost=use_speaker_boost)
        assert result.use_speaker_boost == expected_use_speaker_boost

    @pytest.mark.parametrize(
        ("voice_id", "expected_voice_id"),
        [("test_voice_id", "test_voice_id")],
    )
    def test_set_voice_id(self, elevenlabs_instance, voice_id, expected_voice_id):
        result = elevenlabs_instance.set_voice_id(voice_id)
        assert result.voice_id == expected_voice_id

    @patch("apps.common.eleven_labs.ElevenLabsClient")
    def test_generate_raises_on_api_error(self, mock_client):
        """Test generate raises exception on API error."""
        mock_client.return_value.text_to_speech.convert.side_effect = Exception("API Error")

        with patch.dict("os.environ", {"DJANGO_ELEVENLABS_API_KEY": DEFAULT_API_KEY}):
            instance = ElevenLabs()
        instance.set_text("Test text")

        with pytest.raises(Exception, match="API Error"):
            instance.generate()

    @patch("apps.common.eleven_labs.VoiceSettings")
    @patch("apps.common.eleven_labs.ElevenLabsClient")
    def test_generate_success(self, mock_client, mock_voice_settings):
        mock_client.return_value.text_to_speech.convert.return_value = [b"audio", b"data"]

        with patch.dict("os.environ", {"DJANGO_ELEVENLABS_API_KEY": DEFAULT_API_KEY}):
            instance = ElevenLabs()
        instance.set_text("Test text")
        response = instance.generate()

        assert response == b"audiodata"
        mock_client.return_value.text_to_speech.convert.assert_called_once()

    @patch("apps.common.eleven_labs.ElevenLabsClient")
    def test_save_creates_file(self, mock_client, tmp_path):
        """Test save writes contents to file."""
        with patch.dict("os.environ", {"DJANGO_ELEVENLABS_API_KEY": DEFAULT_API_KEY}):
            instance = ElevenLabs()
        file_path = tmp_path / "output.mp3"
        contents = b"audio_data"

        instance.save(contents, file_path)

        assert file_path.exists()
        assert file_path.read_bytes() == b"audio_data"

    @patch("apps.common.eleven_labs.ElevenLabsClient")
    def test_save_creates_parent_directories(self, mock_client, tmp_path):
        """Test save creates parent directories if they don't exist."""
        with patch.dict("os.environ", {"DJANGO_ELEVENLABS_API_KEY": DEFAULT_API_KEY}):
            instance = ElevenLabs()
        file_path = tmp_path / "nested" / "dir" / "output.mp3"
        contents = b"audio_data"

        instance.save(contents, file_path)

        assert file_path.exists()
        assert file_path.read_bytes() == b"audio_data"
