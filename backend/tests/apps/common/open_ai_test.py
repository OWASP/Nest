from unittest.mock import MagicMock, patch
import openai as openai_module

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
    def test_complete_general_exception(self, mock_openai, mock_logger):
        """Test that general exceptions are caught and logged."""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API error")
        mock_openai.return_value = mock_client
        openai_instance = OpenAi()
        openai_instance.set_prompt("Test prompt").set_input("Test input")
        response = openai_instance.complete()

        assert response is None

        mock_logger.exception.assert_called_once_with(
            "An error occurred during OpenAI API request."
        )

    @patch("apps.common.open_ai.logger")
    @patch("openai.OpenAI")
    def test_complete_api_connection_error(self, mock_openai, mock_logger):
        """Test that APIConnectionError is caught and logged."""
        import openai as openai_module

        mock_client = MagicMock()
        mock_request = MagicMock()
        api_error = openai_module.APIConnectionError(request=mock_request)
        mock_client.chat.completions.create.side_effect = api_error
        mock_openai.return_value = mock_client
        openai_instance = OpenAi()
        openai_instance.set_prompt("Test prompt").set_input("Test input")
        response = openai_instance.complete()

        assert response is None

        mock_logger.exception.assert_called_once_with(
            "A connection error occurred during OpenAI API request."
        )

    @patch("openai.OpenAI")
    def test_complete_success(self, mock_openai):
        """Test successful completion returns the message content."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated response content"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        openai_instance = OpenAi()
        openai_instance.set_prompt("Test prompt").set_input("Test input")
        response = openai_instance.complete()

        assert response == "Generated response content"
        mock_client.chat.completions.create.assert_called_once()
