"""Tests for LLM configuration."""

from unittest.mock import Mock, patch

from apps.ai.common.llm_config import get_llm


class TestLLMConfig:
    """Test cases for LLM configuration."""

    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_openai_default(self, mock_llm, mock_settings):
        """Test getting OpenAI LLM with default model."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPEN_AI_SECRET_KEY = "test-key"  # noqa: S105
        mock_settings.OPEN_AI_MODEL_NAME = "gpt-4o-mini"
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gpt-4o-mini",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_openai_custom_model(self, mock_llm, mock_settings):
        """Test getting OpenAI LLM with custom model."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPEN_AI_SECRET_KEY = "test-key"  # noqa: S105
        mock_settings.OPEN_AI_MODEL_NAME = "gpt-4"
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gpt-4",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.logger")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_unsupported_provider(self, mock_llm, mock_logger, mock_settings):
        """Test getting LLM with unsupported provider logs error and falls back to OpenAI."""
        mock_settings.LLM_PROVIDER = "unsupported"
        mock_settings.OPEN_AI_SECRET_KEY = "test-key"  # noqa: S105
        mock_settings.OPEN_AI_MODEL_NAME = "gpt-4o-mini"
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_logger.error.assert_called_once()
        mock_llm.assert_called_once_with(
            model="gpt-4o-mini",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_google(self, mock_llm, mock_settings):
        """Test getting Google LLM with default model."""
        mock_settings.LLM_PROVIDER = "google"
        mock_settings.GOOGLE_API_KEY = "test-google-key"
        mock_settings.GOOGLE_MODEL_NAME = "gemini-2.0-flash"
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gemini-2.0-flash",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key="test-google-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_google_custom_model(self, mock_llm, mock_settings):
        """Test getting Google LLM with custom model."""
        mock_settings.LLM_PROVIDER = "google"
        mock_settings.GOOGLE_API_KEY = "test-google-key"
        mock_settings.GOOGLE_MODEL_NAME = "gemini-pro"
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gemini-pro",
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key="test-google-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance
