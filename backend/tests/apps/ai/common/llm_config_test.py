"""Tests for LLM configuration."""

import os
from unittest.mock import Mock, patch

from apps.ai.common.llm_config import get_llm


class TestLLMConfig:
    """Test cases for LLM configuration."""

    @patch.dict(os.environ, {"LLM_PROVIDER": "openai"})
    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_openai_default(self, mock_llm, mock_settings):
        """Test getting OpenAI LLM with default model."""
        mock_settings.OPEN_AI_SECRET_KEY = "test-key"  # noqa: S105
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gpt-4o-mini",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_MODEL_NAME": "gpt-4"},
    )
    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_openai_custom_model(self, mock_llm, mock_settings):
        """Test getting OpenAI LLM with custom model."""
        mock_settings.OPEN_AI_SECRET_KEY = "test-key"  # noqa: S105
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gpt-4",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(os.environ, {"LLM_PROVIDER": "unsupported"})
    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.logger")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_unsupported_provider(self, mock_llm, mock_logger, mock_settings):
        """Test getting LLM with unsupported provider logs error and falls back to OpenAI."""
        mock_settings.OPEN_AI_SECRET_KEY = "test-key"  # noqa: S105
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

    @patch.dict(os.environ, {"LLM_PROVIDER": "google"})
    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_google(self, mock_llm, mock_settings):
        """Test getting Google LLM with default model."""
        mock_settings.GOOGLE_API_KEY = "test-google-key"
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gemini/gemini-2.5-flash",
            api_key="test-google-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(
        os.environ,
        {"LLM_PROVIDER": "google", "GOOGLE_MODEL_NAME": "gemini-pro"},
    )
    @patch("apps.ai.common.llm_config.settings")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_google_custom_model(self, mock_llm, mock_settings):
        """Test getting Google LLM with custom model."""
        mock_settings.GOOGLE_API_KEY = "test-google-key"
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gemini/gemini-pro",
            api_key="test-google-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance
