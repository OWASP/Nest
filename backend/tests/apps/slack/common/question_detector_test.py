"""Tests for question detector functionality."""

import math
import os
from unittest.mock import MagicMock, patch

import openai
import pytest
from django.core.exceptions import ObjectDoesNotExist

from apps.slack.common.question_detector import QuestionDetector


class TestQuestionDetector:
    """Test cases for QuestionDetector functionality."""

    @pytest.fixture(autouse=True)
    def _mock_openai(self, monkeypatch):
        """Avoid real OpenAI calls by forcing fallback path."""
        monkeypatch.setenv("DJANGO_OPEN_AI_SECRET_KEY", "test-key")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = openai.OpenAIError("Mocked OpenAI call")

        monkeypatch.setattr("openai.OpenAI", MagicMock(return_value=mock_client))

        # Mock the Retriever class
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []
        monkeypatch.setattr(
            "apps.slack.common.question_detector.Retriever", MagicMock(return_value=mock_retriever)
        )

        monkeypatch.setattr(
            "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
            lambda: "System prompt with {context}",
        )

    @pytest.fixture
    def detector(self, monkeypatch):
        """Fixture to provide QuestionDetector instance."""
        return QuestionDetector()

    @pytest.fixture
    def sample_context_chunks(self):
        """Fixture to provide sample context chunks for testing."""
        return [
            {
                "source_name": "OWASP Top 10",
                "text": (
                    "The OWASP Top 10 is a standard awareness document for developers "
                    "and web application security. It represents a broad consensus about "
                    "the most critical security risks to web applications."
                ),
                "additional_context": {"type": "security_standard", "year": "2021"},
            },
            {
                "source_name": "XSS Prevention",
                "text": (
                    "Cross-Site Scripting (XSS) attacks are a type of injection, "
                    "in which malicious scripts are injected into otherwise benign "
                    "and trusted web sites."
                ),
                "additional_context": {"risk_level": "high", "category": "injection"},
            },
        ]

    def test_init(self, detector):
        """Test QuestionDetector initialization."""
        # Test that detector initializes properly
        assert detector is not None
        assert hasattr(detector, "openai_client")
        assert hasattr(detector, "retriever")

    def test_is_owasp_question_true_cases(self, detector, sample_context_chunks, monkeypatch):
        """Test cases that should be detected as OWASP questions."""
        # Mock OpenAI to return True for OWASP questions
        mock_openai_method = MagicMock(return_value=True)
        monkeypatch.setattr(detector, "is_owasp_question_with_openai", mock_openai_method)

        assert detector.is_owasp_question("What is owasp?")
        assert detector.is_owasp_question("How do I fix security vulnerabilities?")
        assert detector.is_owasp_question("Can you explain xss attacks?")
        assert detector.is_owasp_question("What are the owasp top 10?")
        assert detector.is_owasp_question("How does webgoat work?")
        assert detector.is_owasp_question("Tell me about application security")
        assert detector.is_owasp_question("I need help with threat modeling")
        assert detector.is_owasp_question("Can you recommend secure coding practices?")

    def test_is_owasp_question_false_cases(self, detector, sample_context_chunks, monkeypatch):
        """Test cases that should not be detected as OWASP questions."""
        # Mock OpenAI to return False for non-OWASP questions
        mock_openai_method = MagicMock(return_value=False)
        monkeypatch.setattr(detector, "is_owasp_question_with_openai", mock_openai_method)

        assert not detector.is_owasp_question("What is Python?")
        assert not detector.is_owasp_question("How do I cook pasta?")

        # Test non-questions (should return False regardless of OpenAI result)
        assert not detector.is_owasp_question("OWASP is great")
        assert not detector.is_owasp_question("Security is important")
        assert not detector.is_owasp_question("OWASP provides security resources")
        assert not detector.is_owasp_question("Vulnerabilities are common")

    def test_is_owasp_question_empty_or_none(self, detector):
        """Test handling of empty or None input."""
        assert not detector.is_owasp_question("")
        assert not detector.is_owasp_question("   ")
        assert not detector.is_owasp_question(None)

    def test_case_insensitive_detection(self, detector, monkeypatch):
        """Test that detection is case insensitive."""
        # Mock OpenAI to return True for OWASP questions
        mock_openai_method = MagicMock(return_value=True)
        monkeypatch.setattr(detector, "is_owasp_question_with_openai", mock_openai_method)

        assert detector.is_owasp_question("WHAT IS OWASP?")
        assert detector.is_owasp_question("what is owasp?")
        assert detector.is_owasp_question("What Is OWASP?")
        assert detector.is_owasp_question("How Do I Fix SECURITY Vulnerabilities?")

    def test_question_with_special_characters(self, detector, monkeypatch):
        """Test question detection with special characters."""
        # Mock OpenAI to return True for OWASP questions
        mock_openai_method = MagicMock(return_value=True)
        monkeypatch.setattr(detector, "is_owasp_question_with_openai", mock_openai_method)

        assert detector.is_owasp_question("What is xss & how to prevent it?")
        assert detector.is_owasp_question("Can you explain sql injection (SQLi)?")
        assert detector.is_owasp_question("What's the best owasp tool?")
        assert detector.is_owasp_question("How do I use webgoat 2.0?")

    def test_whitespace_handling(self, detector, monkeypatch):
        """Test proper handling of whitespace in questions."""
        # Mock OpenAI to return True for OWASP questions
        mock_openai_method = MagicMock(return_value=True)
        monkeypatch.setattr(detector, "is_owasp_question_with_openai", mock_openai_method)

        assert detector.is_owasp_question("  What is owasp?  ")
        assert detector.is_owasp_question("\tHow does security work?\n")
        assert detector.is_owasp_question("What\nis\nowasp?")

    @pytest.mark.parametrize(
        "question",
        [
            "What are the main differences between SAST and DAST security testing approaches?",
            "How can I integrate OWASP ZAP into my CI/CD pipeline for automated security testing?",
            "What are the best practices for preventing injection attacks in web applications?",
            "Can you explain the OWASP Risk Rating Methodology and how to apply it?",
            "Which OWASP project would you recommend for threat modeling enterprise applications?",
            (
                "How do I implement proper authentication and session management "
                "following OWASP guidelines?"
            ),
        ],
    )
    def test_complex_owasp_questions(self, detector, question, monkeypatch):
        """Test complex real-world OWASP questions."""
        # Mock OpenAI to return True for OWASP questions
        mock_openai_method = MagicMock(return_value=True)
        monkeypatch.setattr(detector, "is_owasp_question_with_openai", mock_openai_method)

        assert detector.is_owasp_question(question.lower()), f"Failed for: {question}"

    def test_mocked_initialization(self):
        """Test with mocked QuestionDetector initialization."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
        ):
            mock_openai.return_value = MagicMock()
            detector = QuestionDetector()

            # Test that detector initializes properly
            assert detector is not None
            assert hasattr(detector, "openai_client")
            assert hasattr(detector, "retriever")

    def test_class_constants(self, detector):
        """Test that class constants are properly defined."""
        assert detector.MAX_TOKENS == 10
        assert math.isclose(detector.TEMPERATURE, 0.1)
        assert detector.CHAT_MODEL == "gpt-4o-mini"

    def test_openai_client_initialization(self, detector):
        """Test that OpenAI client is properly initialized."""
        assert detector.openai_client is not None
        assert hasattr(detector.openai_client, "chat")

    def test_is_owasp_question_with_openai_missing_prompt(self):
        """Test OpenAI question detection when prompt is missing."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value=None,
            ),
        ):
            detector = QuestionDetector()

            with pytest.raises(
                ObjectDoesNotExist,
                match="Prompt with key 'slack-question-detector-system-prompt' not found",
            ):
                detector.is_owasp_question_with_openai("What is OWASP?", [])

    def test_is_owasp_question_with_openai_empty_prompt(self):
        """Test OpenAI question detection when prompt is empty."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="   ",
            ),
        ):
            detector = QuestionDetector()

            with pytest.raises(
                ObjectDoesNotExist,
                match="Prompt with key 'slack-question-detector-system-prompt' not found",
            ):
                detector.is_owasp_question_with_openai("What is OWASP?", [])

    def test_is_owasp_question_with_openai_success_yes(self, sample_context_chunks):
        """Test OpenAI question detection with YES response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "YES"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is OWASP?", sample_context_chunks
            )

            assert result is True

    def test_is_owasp_question_with_openai_success_no(self, sample_context_chunks):
        """Test OpenAI question detection with NO response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "NO"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is Python?", sample_context_chunks
            )

            assert result is False

    def test_is_owasp_question_with_openai_empty_response(self, sample_context_chunks):
        """Test OpenAI question detection with empty response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = ""
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is OWASP?", sample_context_chunks
            )

            assert result is None

    def test_is_owasp_question_with_openai_none_response(self, sample_context_chunks):
        """Test OpenAI question detection with None response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = None
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is OWASP?", sample_context_chunks
            )

            assert result is None

    def test_is_owasp_question_with_openai_unexpected_response(self, sample_context_chunks):
        """Test OpenAI question detection with unexpected response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "MAYBE"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is OWASP?", sample_context_chunks
            )

            assert result is None

    def test_is_owasp_question_with_openai_api_error(self, sample_context_chunks):
        """Test OpenAI question detection with API error."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = openai.OpenAIError("API Error")
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is OWASP?", sample_context_chunks
            )

            assert result is None

    def test_is_owasp_question_with_openai_case_insensitive(self, sample_context_chunks):
        """Test OpenAI question detection with case insensitive responses."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "yes, this is OWASP related"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is OWASP?", sample_context_chunks
            )

            assert result is True

    def test_is_owasp_question_with_openai_no_in_response(self, sample_context_chunks):
        """Test OpenAI question detection with 'no' in response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {context}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "no, this is not OWASP related"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai(
                "What is Python?", sample_context_chunks
            )

            assert result is False

    def test_format_context_chunks(self, detector, sample_context_chunks):
        """Test formatting of context chunks."""
        formatted = detector.format_context_chunks(sample_context_chunks)

        assert "Source Name: OWASP Top 10" in formatted
        assert "Source Name: XSS Prevention" in formatted
        assert "The OWASP Top 10 is a standard awareness document" in formatted
        assert "Cross-Site Scripting (XSS) attacks are a type of injection" in formatted
        assert "---" in formatted  # Separator between chunks

    def test_format_context_chunks_empty(self, detector):
        """Test formatting of empty context chunks."""
        formatted = detector.format_context_chunks([])
        assert formatted == "No context provided"

    def test_format_context_chunks_none(self, detector):
        """Test formatting of None context chunks."""
        formatted = detector.format_context_chunks(None)
        assert formatted == "No context provided"

    def test_format_context_chunks_without_additional_context(self, detector):
        """Test formatting of context chunks without additional_context."""
        chunks = [
            {
                "source_name": "Test Source",
                "text": "Some content here",
            }
        ]
        formatted = detector.format_context_chunks(chunks)

        assert "Source Name: Test Source" in formatted
        assert "Content: Some content here" in formatted
        assert "Additional Context:" not in formatted

    def test_initialization_without_api_key(self, monkeypatch):
        """Test QuestionDetector initialization without API key."""
        monkeypatch.delenv("DJANGO_OPEN_AI_SECRET_KEY", raising=False)

        with pytest.raises(
            ValueError, match="DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
        ):
            QuestionDetector()

    def test_is_owasp_question_with_openai_none_logs_warning(
        self, detector, sample_context_chunks, monkeypatch
    ):
        """Test that None result from OpenAI logs a warning."""
        # Mock OpenAI to return None
        mock_openai_method = MagicMock(return_value=None)
        monkeypatch.setattr(detector, "is_owasp_question_with_openai", mock_openai_method)

        # Mock logger to capture warning
        with patch("apps.slack.common.question_detector.logger") as mock_logger:
            result = detector.is_owasp_question("What is OWASP?")

            # Should log warning when OpenAI detection returns None
            mock_logger.warning.assert_called_with("OpenAI detection failed.")
            assert result is False
