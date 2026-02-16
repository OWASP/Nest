"""Tests for LLM configuration."""

import os
from unittest.mock import Mock, patch

from apps.ai.common.llm_config import get_llm


class TestLLMConfig:
    """Test cases for LLM configuration."""

    @patch.dict(
        os.environ,
        {"DJANGO_LLM_PROVIDER": "openai", "DJANGO_OPEN_AI_SECRET_KEY": "test-key"},
    )
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_openai_default(self, mock_llm):
        """Test getting OpenAI LLM with default model."""
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
        {
            "DJANGO_LLM_PROVIDER": "openai",
            "DJANGO_OPEN_AI_SECRET_KEY": "test-key",
            "DJANGO_OPEN_AI_MODEL_NAME": "gpt-4",
        },
    )
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_openai_custom_model(self, mock_llm):
        """Test getting OpenAI LLM with custom model."""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gpt-4",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(
        os.environ,
        {
            "DJANGO_LLM_PROVIDER": "unsupported",
            "DJANGO_OPEN_AI_SECRET_KEY": "test-key",
        },
    )
    @patch("apps.ai.common.llm_config.logger")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_unsupported_provider(self, mock_llm, mock_logger):
        """Test getting LLM with unsupported provider logs error and falls back to OpenAI."""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        # Should log error about unrecognized provider
        mock_logger.error.assert_called_once()
        # Should fallback to OpenAI
        mock_llm.assert_called_once_with(
            model="gpt-4o-mini",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(
        os.environ,
        {
            "DJANGO_LLM_PROVIDER": "google",
            "DJANGO_GOOGLE_API_KEY": "test-google-key",
        },
    )
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_google(self, mock_llm):
        """Test getting Google LLM with default model."""
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

    @patch.dict(
        os.environ,
        {
            "DJANGO_LLM_PROVIDER": "google",
            "DJANGO_GOOGLE_API_KEY": "test-google-key",
            "DJANGO_GOOGLE_MODEL_NAME": "gemini-pro",
        },
    )
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_google_custom_model(self, mock_llm):
        """Test getting Google LLM with custom model."""
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
