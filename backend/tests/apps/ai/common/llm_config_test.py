"""Tests for LLM configuration."""

import os
from unittest.mock import Mock, patch

from apps.ai.common.llm_config import get_llm


class TestLLMConfig:
    """Test cases for LLM configuration."""

    @patch.dict(os.environ, {"LLM_PROVIDER": "openai", "DJANGO_OPEN_AI_SECRET_KEY": "test-key"})
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_openai_default(self, mock_llm):
        """Test getting OpenAI LLM with default model."""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        mock_llm.assert_called_once_with(
            model="gpt-4.1-mini",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "openai",
            "DJANGO_OPEN_AI_SECRET_KEY": "test-key",
            "OPENAI_MODEL_NAME": "gpt-4",
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
            "LLM_PROVIDER": "anthropic",
            "DJANGO_OPEN_AI_SECRET_KEY": "test-key",
        },
    )
    @patch("apps.ai.common.llm_config.logger")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_anthropic_default(self, mock_llm, mock_logger):
        """Test getting LLM with unsupported Anthropic provider falls back to OpenAI."""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        # Should log warning about unrecognized provider
        mock_logger.warning.assert_called_once()
        # Should fallback to OpenAI
        mock_llm.assert_called_once_with(
            model="gpt-4.1-mini",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "anthropic",
            "DJANGO_OPEN_AI_SECRET_KEY": "test-key",
            "OPENAI_MODEL_NAME": "gpt-4",
        },
    )
    @patch("apps.ai.common.llm_config.logger")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_anthropic_custom_model(self, mock_llm, mock_logger):
        """Test getting LLM with unsupported Anthropic provider falls back to OpenAI."""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        # Should log warning about unrecognized provider
        mock_logger.warning.assert_called_once()
        # Should fallback to OpenAI with custom model
        mock_llm.assert_called_once_with(
            model="gpt-4",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance

    @patch.dict(
        os.environ,
        {
            "LLM_PROVIDER": "unsupported",
            "DJANGO_OPEN_AI_SECRET_KEY": "test-key",
        },
    )
    @patch("apps.ai.common.llm_config.logger")
    @patch("apps.ai.common.llm_config.LLM")
    def test_get_llm_unsupported_provider(self, mock_llm, mock_logger):
        """Test getting LLM with unsupported provider logs warning and falls back to OpenAI."""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        result = get_llm()

        # Should log warning about unrecognized provider
        mock_logger.warning.assert_called_once()
        # Should fallback to OpenAI
        mock_llm.assert_called_once_with(
            model="gpt-4.1-mini",
            api_key="test-key",
            temperature=0.1,
        )
        assert result == mock_llm_instance
