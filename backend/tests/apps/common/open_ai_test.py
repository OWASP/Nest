from unittest.mock import MagicMock, patch

import openai
import pytest

from apps.common.open_ai import OpenAi

DEFAULT_MAX_TOKENS = 1000
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TIMEOUT = 30
DEFAULT_API_KEY = "test_secret_key"
DEFAULT_MAX_TOKENS_SET = 2000
TEST_PROMPT = "Test prompt"
TEST_INPUT = "Test input"
TEST_RESPONSE = "Test response"
ERROR_MESSAGE = "An error occurred during OpenAI API request."
SETTINGS_PATH = "apps.common.open_ai.settings"
DEFAULT_TEST_PROMPT = "Test prompt"


class TestOpenAi:
    @pytest.fixture
    def openai_instance(self, monkeypatch):
        mock_settings = type("obj", (object,), {"OPEN_AI_SECRET_KEY": DEFAULT_API_KEY})
        monkeypatch.setattr(SETTINGS_PATH, mock_settings)
        return OpenAi()

    @patch(SETTINGS_PATH)
    @patch("openai.OpenAI")
    def test_init(self, mock_openai, mock_settings):
        mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY

        instance = OpenAi()

        mock_openai.assert_called_once_with(api_key=DEFAULT_API_KEY, timeout=DEFAULT_TIMEOUT)
        assert instance.max_tokens == DEFAULT_MAX_TOKENS
        assert instance.model == DEFAULT_MODEL
        assert instance.temperature == DEFAULT_TEMPERATURE

    @patch("openai.OpenAI")
    def test_init_direct_call(self, mock_openai):
        """Test direct initialization with actual client creation."""
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY
            instance = OpenAi()
            assert isinstance(instance.client, MagicMock)
            assert instance.max_tokens == DEFAULT_MAX_TOKENS
            assert instance.model == DEFAULT_MODEL
            assert instance.temperature == DEFAULT_TEMPERATURE

    @pytest.mark.parametrize(
        ("input_content", "expected_input"),
        [("Test input content", "Test input content"), ("", "")],
    )
    def test_set_input(self, openai_instance, input_content, expected_input):
        result = openai_instance.set_input(input_content)
        assert result.input == expected_input
        assert result is openai_instance

    def test_set_input_direct(self):
        """Directly test set_input to ensure full coverage."""
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY
            instance = OpenAi()
            instance.set_input("Test")
            assert instance.input == "Test"

    @pytest.mark.parametrize(
        ("max_tokens", "expected_max_tokens"),
        [(DEFAULT_MAX_TOKENS_SET, DEFAULT_MAX_TOKENS_SET), (0, 0), (None, None)],
    )
    def test_set_max_tokens(self, openai_instance, max_tokens, expected_max_tokens):
        result = openai_instance.set_max_tokens(max_tokens)
        assert result.max_tokens == expected_max_tokens
        assert result is openai_instance

    def test_set_max_tokens_direct(self):
        """Directly test set_max_tokens to ensure full coverage."""
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY
            instance = OpenAi()
            instance.set_max_tokens(500)
            token_count = 500
            assert instance.max_tokens == token_count

    @pytest.mark.parametrize(
        ("prompt_content", "expected_prompt"),
        [("Test prompt content", "Test prompt content"), ("", ""), (None, None)],
    )
    def test_set_prompt(self, openai_instance, prompt_content, expected_prompt):
        result = openai_instance.set_prompt(prompt_content)
        assert result.prompt == expected_prompt
        assert result is openai_instance

    def test_set_prompt_direct(self):
        """Directly test set_prompt to ensure full coverage."""
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY
            instance = OpenAi()
            instance.set_prompt(DEFAULT_TEST_PROMPT)
            assert instance.prompt == DEFAULT_TEST_PROMPT

    def test_method_chaining(self, openai_instance):
        result = (
            openai_instance.set_prompt(DEFAULT_TEST_PROMPT)
            .set_input(TEST_INPUT)
            .set_max_tokens(DEFAULT_MAX_TOKENS_SET)
        )

        assert result is openai_instance
        assert result.prompt == DEFAULT_TEST_PROMPT
        assert result.input == TEST_INPUT
        assert result.max_tokens == DEFAULT_MAX_TOKENS_SET

    @patch("apps.common.open_ai.logger")
    @patch("openai.OpenAI")
    def test_complete_api_connection_error(self, mock_openai, mock_logger, openai_instance):
        openai_instance.client = mock_openai.return_value
        mock_openai.return_value.chat.completions.create.side_effect = openai.APIConnectionError(
            request=None
        )

        openai_instance.set_prompt(TEST_PROMPT).set_input(TEST_INPUT)
        response = openai_instance.complete()

        assert response is None
        mock_logger.exception.assert_called_once_with(ERROR_MESSAGE)

    @patch("apps.common.open_ai.logger")
    @patch("openai.OpenAI")
    def test_complete_general_exception(self, mock_openai, mock_logger, openai_instance):
        openai_instance.client = mock_openai.return_value
        mock_openai.return_value.chat.completions.create.side_effect = Exception()

        openai_instance.set_prompt(TEST_PROMPT).set_input(TEST_INPUT)
        response = openai_instance.complete()

        assert response is None
        mock_logger.exception.assert_called_once_with(ERROR_MESSAGE)

    @patch("openai.OpenAI")
    def test_complete_successful(self, mock_openai, openai_instance):
        mock_client = mock_openai.return_value
        mock_response = mock_client.chat.completions.create.return_value
        mock_response.choices = [
            type("obj", (object,), {"message": type("obj", (object,), {"content": TEST_RESPONSE})})
        ]

        openai_instance.client = mock_client
        openai_instance.set_prompt(DEFAULT_TEST_PROMPT).set_input(TEST_INPUT)
        response = openai_instance.complete()

        assert response == TEST_RESPONSE
        mock_client.chat.completions.create.assert_called_once_with(
            max_tokens=DEFAULT_MAX_TOKENS,
            messages=[
                {"role": "system", "content": DEFAULT_TEST_PROMPT},
                {"role": "user", "content": TEST_INPUT},
            ],
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
        )

    @patch("openai.OpenAI")
    def test_complete_with_actual_input(self, mock_openai):
        """Test complete method with actual inputs and execution."""
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY
            instance = OpenAi()

            mock_client = MagicMock()
            instance.client = mock_client

            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            mock_message.content = TEST_RESPONSE
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]

            mock_client.chat.completions.create.return_value = mock_response

            instance.prompt = DEFAULT_TEST_PROMPT
            instance.input = TEST_INPUT

            result = instance.complete()

            assert result == TEST_RESPONSE
            mock_client.chat.completions.create.assert_called_once_with(
                max_tokens=DEFAULT_MAX_TOKENS,
                messages=[
                    {"role": "system", "content": DEFAULT_TEST_PROMPT},
                    {"role": "user", "content": TEST_INPUT},
                ],
                model=DEFAULT_MODEL,
                temperature=DEFAULT_TEMPERATURE,
            )

    @patch("apps.common.open_ai.logger")
    def test_complete_api_connection_error_direct(self, mock_logger):
        """Direct test for APIConnectionError in complete method."""
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY

            instance = OpenAi()

            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = openai.APIConnectionError(
                request=None
            )
            instance.client = mock_client

            instance.prompt = DEFAULT_TEST_PROMPT
            instance.input = TEST_INPUT

            result = instance.complete()

            assert result is None
            mock_logger.exception.assert_called_once_with(ERROR_MESSAGE)

    @patch("apps.common.open_ai.logger")
    def test_complete_general_exception_direct(self, mock_logger):
        """Direct test for general Exception in complete method."""
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY

            instance = OpenAi()

            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("General error")
            instance.client = mock_client

            instance.prompt = DEFAULT_TEST_PROMPT
            instance.input = TEST_INPUT

            result = instance.complete()

            assert result is None
            mock_logger.exception.assert_called_once_with(ERROR_MESSAGE)

    @pytest.mark.parametrize(
        ("model", "max_tokens", "temperature"),
        [
            ("gpt-4", 500, 0.5),
            ("gpt-3.5-turbo", 200, 0.0),
            (DEFAULT_MODEL, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE),
        ],
    )
    def test_constructor_with_parameters(self, model, max_tokens, temperature):
        with patch(SETTINGS_PATH) as mock_settings:
            mock_settings.OPEN_AI_SECRET_KEY = DEFAULT_API_KEY

            instance = OpenAi(model=model, max_tokens=max_tokens, temperature=temperature)

            assert instance.model == model
            assert instance.max_tokens == max_tokens
            assert instance.temperature == temperature

    @pytest.mark.parametrize(
        ("model", "expected_model"),
        [("gpt-4", "gpt-4"), ("gpt-3.5-turbo", "gpt-3.5-turbo"), (DEFAULT_MODEL, DEFAULT_MODEL)],
    )
    def test_custom_model(self, model, expected_model):
        instance = OpenAi(model=model)
        assert instance.model == expected_model

    @pytest.mark.parametrize(
        ("temperature", "expected_temperature"),
        [(0.5, 0.5), (0.0, 0.0), (1.0, 1.0), (DEFAULT_TEMPERATURE, DEFAULT_TEMPERATURE)],
    )
    def test_custom_temperature(self, temperature, expected_temperature):
        instance = OpenAi(temperature=temperature)
        assert instance.temperature == expected_temperature
