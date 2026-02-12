from unittest.mock import patch

import pytest

from apps.common.open_ai import OpenAi

# Constants to replace magic values
DEFAULT_MAX_TOKENS = 1000
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 30
DEFAULT_API_KEY = "test_secret_key"
DEFAULT_MAX_TOKENS_SET = 2000


class TestOpenAi:
    @pytest.fixture
    def openai_instance(self):
        return OpenAi()

    @patch("apps.common.open_ai.settings")
    @patch("openai.OpenAI")
    def test_init(self, mock_openai, mock_settings):
        mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY

        instance = OpenAi()

        mock_openai.assert_called_once_with(api_key=DEFAULT_API_KEY, timeout=DEFAULT_TIMEOUT)
        assert instance.max_tokens == DEFAULT_MAX_TOKENS
        assert instance.model == DEFAULT_MODEL
        assert instance.temperature == DEFAULT_TEMPERATURE

    def test_set_images(self, openai_instance):
        """Test set_images stores images and returns self for chaining."""
        images = ["data:image/png;base64,abc123"]
        result = openai_instance.set_images(images)

        assert result is openai_instance
        assert openai_instance.images == images

    @pytest.mark.parametrize(
        ("input_content", "expected_input"), [("Test input content", "Test input content")]
    )
    def test_set_input(self, openai_instance, input_content, expected_input):
        result = openai_instance.set_input(input_content)
        assert result.input == expected_input

    @pytest.mark.parametrize(
        ("max_tokens", "expected_max_tokens"), [(DEFAULT_MAX_TOKENS_SET, DEFAULT_MAX_TOKENS_SET)]
    )
    def test_set_max_tokens(self, openai_instance, max_tokens, expected_max_tokens):
        result = openai_instance.set_max_tokens(max_tokens)
        assert result.max_tokens == expected_max_tokens

    @pytest.mark.parametrize(
        ("prompt_content", "expected_prompt"), [("Test prompt content", "Test prompt content")]
    )
    def test_set_prompt(self, openai_instance, prompt_content, expected_prompt):
        result = openai_instance.set_prompt(prompt_content)
        assert result.prompt == expected_prompt

    @patch("apps.common.open_ai.logger")
    @patch("openai.OpenAI")
    def test_complete_general_exception(self, mock_openai, mock_logger, openai_instance):
        mock_openai.return_value.chat.completions.create.side_effect = Exception()

        openai_instance.set_prompt("Test prompt").set_input("Test input")
        response = openai_instance.complete()

        assert response is None

        mock_logger.exception.assert_called_once_with(
            "An error occurred during OpenAI API request."
        )

    def test_user_content_text_only(self, openai_instance):
        """Test user_content returns text-only content when no images."""
        openai_instance.set_input("What is OWASP?")

        content = openai_instance.user_content

        assert isinstance(content, list)
        assert len(content) == 1
        assert content[0] == {"type": "text", "text": "What is OWASP?"}

    def test_user_content_with_images(self, openai_instance):
        """Test user_content returns multimodal content list with images."""
        openai_instance.set_input("What is in this image?")
        openai_instance.set_images(["data:image/png;base64,abc123"])

        content = openai_instance.user_content

        assert isinstance(content, list)
        assert len(content) == 2
        assert content[0] == {"type": "text", "text": "What is in this image?"}
        assert content[1] == {
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64,abc123"},
        }

    def test_user_content_with_multiple_images(self, openai_instance):
        """Test user_content with multiple images."""
        openai_instance.set_input("Describe these images")
        openai_instance.set_images(
            [
                "data:image/png;base64,img1",
                "data:image/jpeg;base64,img2",
            ]
        )

        content = openai_instance.user_content

        assert isinstance(content, list)
        assert len(content) == 3
        assert content[0] == {"type": "text", "text": "Describe these images"}
        assert content[1]["type"] == "image_url"
        assert content[2]["type"] == "image_url"
