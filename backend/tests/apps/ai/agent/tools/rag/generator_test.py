"""Tests for the RAG Generator."""

import os
from unittest.mock import MagicMock, patch

import openai
import pytest
from django.core.exceptions import ObjectDoesNotExist

from apps.ai.agent.tools.rag.generator import Generator


class TestGenerator:
    """Test cases for the Generator class."""

    def test_init_success(self):
        """Test successful initialization with API key."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            generator = Generator(chat_model="gpt-4")

            assert generator.chat_model == "gpt-4"
            assert generator.openai_client == mock_client
            mock_openai.assert_called_once_with(api_key="test-key")

    def test_init_no_api_key(self):
        """Test initialization fails when API key is not set."""
        with (
            patch.dict(os.environ, {}, clear=True),
            pytest.raises(
                ValueError,
                match="DJANGO_OPEN_AI_SECRET_KEY environment variable not set",
            ),
        ):
            Generator()

    def test_prepare_context_empty_chunks(self):
        """Test context preparation with empty chunks list."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            generator = Generator()

            result = generator.prepare_context([])

            assert result == "No context provided"

    def test_prepare_context_with_chunks(self):
        """Test context preparation with valid chunks."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            generator = Generator()

            chunks = [
                {"source_name": "Chapter 1", "text": "This is chapter 1 content"},
                {"source_name": "Chapter 2", "text": "This is chapter 2 content"},
            ]

            result = generator.prepare_context(chunks)

            expected = (
                "Source Name: Chapter 1\nContent: This is chapter 1 content\n\n"
                "---\n\n"
                "Source Name: Chapter 2\nContent: This is chapter 2 content"
            )
            assert result == expected

    def test_prepare_context_missing_fields(self):
        """Test context preparation with chunks missing fields."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI"),
        ):
            generator = Generator()

            chunks = [
                {"text": "Content without source"},
                {"source_name": "Source without content"},
                {},
            ]

            result = generator.prepare_context(chunks)

            expected = (
                "Source Name: Unknown Source 1\nContent: Content without source\n\n"
                "---\n\n"
                "Source Name: Source without content\nContent: \n\n"
                "---\n\n"
                "Source Name: Unknown Source 3\nContent: "
            )
            assert result == expected

    def test_generate_answer_success(self):
        """Test successful answer generation."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="System prompt",
            ),
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Generated answer"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            generator = Generator()

            chunks = [{"source_name": "Test", "text": "Test content"}]
            result = generator.generate_answer("What is OWASP?", chunks)

            assert result == "Generated answer"
            mock_client.chat.completions.create.assert_called_once()
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]["model"] == "gpt-4o"
            assert len(call_args[1]["messages"]) == 2
            assert call_args[1]["messages"][0]["role"] == "system"
            assert call_args[1]["messages"][1]["role"] == "user"

    def test_generate_answer_with_custom_model(self):
        """Test answer generation with custom chat model."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="System prompt",
            ),
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Custom model answer"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            generator = Generator(chat_model="gpt-3.5-turbo")

            chunks = [{"source_name": "Test", "text": "Test content"}]
            result = generator.generate_answer("Test query", chunks)

            assert result == "Custom model answer"
            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]["model"] == "gpt-3.5-turbo"

    def test_generate_answer_openai_error(self):
        """Test answer generation with OpenAI API error."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="System prompt",
            ),
        ):
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = openai.OpenAIError("API Error")
            mock_openai.return_value = mock_client

            generator = Generator()

            chunks = [{"source_name": "Test", "text": "Test content"}]
            result = generator.generate_answer("Test query", chunks)

            assert result == "I'm sorry, I'm currently unable to process your request."

    def test_generate_answer_with_empty_chunks(self):
        """Test answer generation with empty chunks."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="System prompt",
            ),
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "No context answer"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            generator = Generator()

            result = generator.generate_answer("Test query", [])

            assert result == "No context answer"
            call_args = mock_client.chat.completions.create.call_args
            assert "No context provided" in call_args[1]["messages"][1]["content"]

    def test_system_prompt_content(self):
        """Test that system prompt passed to OpenAI comes from Prompt getter."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="OWASP Foundation system prompt",
            ) as mock_prompt_getter,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Answer"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            generator = Generator()
            generator.generate_answer("Q", [])

            call_args = mock_client.chat.completions.create.call_args
            assert call_args[1]["messages"][0]["role"] == "system"
            assert call_args[1]["messages"][0]["content"] == "OWASP Foundation system prompt"
            mock_prompt_getter.assert_called_once()

    def test_generate_answer_missing_system_prompt(self):
        """Test answer generation when system prompt is missing."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value=None,
            ),
        ):
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            generator = Generator()

            chunks = [{"source_name": "Test", "text": "Test content"}]

            with pytest.raises(
                ObjectDoesNotExist, match="Prompt with key 'rag-system-prompt' not found"
            ):
                generator.generate_answer("Test query", chunks)

    def test_generate_answer_empty_system_prompt(self):
        """Test answer generation when system prompt is empty."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="   ",
            ),
        ):
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            generator = Generator()

            chunks = [{"source_name": "Test", "text": "Test content"}]

            with pytest.raises(
                ObjectDoesNotExist, match="Prompt with key 'rag-system-prompt' not found"
            ):
                generator.generate_answer("Test query", chunks)

    def test_generate_answer_empty_openai_response(self):
        """Test answer generation when OpenAI returns empty content."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="System prompt",
            ),
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = ""
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            generator = Generator()

            chunks = [{"source_name": "Test", "text": "Test content"}]
            result = generator.generate_answer("Test query", chunks)

            assert result == ""

    def test_generate_answer_none_openai_response(self):
        """Test answer generation when OpenAI returns None content."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.core.models.prompt.Prompt.get_rag_system_prompt",
                return_value="System prompt",
            ),
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = None
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            generator = Generator()

            chunks = [{"source_name": "Test", "text": "Test content"}]

            with pytest.raises(AttributeError):
                generator.generate_answer("Test query", chunks)

    def test_constants(self):
        """Test class constants have expected values."""
        assert Generator.MAX_TOKENS == 2000
        assert Generator.TEMPERATURE == 0.4
