"""Tests for question detector functionality."""

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

        monkeypatch.setattr(
            "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
            lambda: "System prompt with {keywords}",
        )

    @pytest.fixture
    def detector(self, monkeypatch):
        """Fixture to provide QuestionDetector instance."""
        return QuestionDetector()

    def test_init(self, detector):
        """Test QuestionDetector initialization."""
        assert detector.owasp_keywords is not None
        assert len(detector.compiled_patterns) == 4

    def test_is_question_with_question_mark(self, detector):
        """Test question detection with question mark."""
        assert detector.is_question("What is OWASP?")
        assert detector.is_question("How does security work?")
        assert detector.is_question("Is this secure?")

    def test_is_question_with_question_words(self, detector):
        """Test question detection with question words."""
        assert detector.is_question("What is security")
        assert detector.is_question("How can I help")
        assert detector.is_question("Why does this happen")
        assert detector.is_question("When should I use this")
        assert detector.is_question("Where can I find documentation")
        assert detector.is_question("Which tool is better")
        assert detector.is_question("Who can help me")
        assert detector.is_question("Can you explain")
        assert detector.is_question("Could this work")
        assert detector.is_question("Would you recommend")
        assert detector.is_question("Should I use this")
        assert detector.is_question("Is this correct")
        assert detector.is_question("Are there alternatives")
        assert detector.is_question("Does this work")
        assert detector.is_question("Do you know")
        assert detector.is_question("Did this happen")

    def test_is_question_with_help_words(self, detector):
        """Test question detection with help-related words."""
        assert detector.is_question("Please help me with security")
        assert detector.is_question("Can you explain this concept")
        assert detector.is_question("Tell me about OWASP")
        assert detector.is_question("Show me an example")
        assert detector.is_question("I need a guide")
        assert detector.is_question("Looking for a tutorial")

    def test_is_question_with_advice_words(self, detector):
        """Test question detection with advice-related words."""
        assert detector.is_question("I recommend this approach")
        assert detector.is_question("Can you suggest something")
        assert detector.is_question("What's your advice")
        assert detector.is_question("Need your opinion")

    def test_is_question_false_cases(self, detector):
        """Test cases that should not be detected as questions."""
        assert not detector.is_question("This is a statement")
        assert not detector.is_question("OWASP is great")
        assert not detector.is_question("Security vulnerabilities exist")
        assert not detector.is_question("Hello everyone")
        assert not detector.is_question("Thanks for your assistance")

    def test_contains_owasp_keywords_single_words(self, detector):
        """Test OWASP keyword detection with single words."""
        assert detector.contains_owasp_keywords("owasp security")
        assert detector.contains_owasp_keywords("vulnerability assessment")
        assert detector.contains_owasp_keywords("webgoat tool")
        assert detector.contains_owasp_keywords("appsec testing")
        assert detector.contains_owasp_keywords("devsecops pipeline")
        assert detector.contains_owasp_keywords("xss attack")
        assert detector.contains_owasp_keywords("csrf protection")
        assert detector.contains_owasp_keywords("injection prevention")

    def test_contains_owasp_keywords_multi_word_phrases(self, detector):
        """Test OWASP keyword detection with multi-word phrases."""
        assert detector.contains_owasp_keywords("threat modeling process")
        assert detector.contains_owasp_keywords("defectdojo tool")
        assert detector.contains_owasp_keywords("juice shop example")
        assert detector.contains_owasp_keywords("red team exercise")
        assert detector.contains_owasp_keywords("application security testing")
        assert detector.contains_owasp_keywords("web security best practices")
        assert detector.contains_owasp_keywords("mobile security guidelines")
        assert detector.contains_owasp_keywords("api security framework")

    def test_contains_owasp_keywords_false_cases(self, detector):
        """Test cases that should not contain OWASP keywords."""
        assert not detector.contains_owasp_keywords("hello world")
        assert not detector.contains_owasp_keywords("python programming")
        assert not detector.contains_owasp_keywords("weather forecast")
        assert not detector.contains_owasp_keywords("random conversation")

    def test_is_owasp_question_true_cases(self, detector):
        """Test cases that should be detected as OWASP questions."""
        assert detector.is_owasp_question("What is owasp?")
        assert detector.is_owasp_question("How do I fix security vulnerabilities?")
        assert detector.is_owasp_question("Can you explain xss attacks?")
        assert detector.is_owasp_question("What are the owasp top 10?")
        assert detector.is_owasp_question("How does webgoat work?")
        assert detector.is_owasp_question("Tell me about application security")
        assert detector.is_owasp_question("I need help with threat modeling")
        assert detector.is_owasp_question("Can you recommend secure coding practices?")

    def test_is_owasp_question_false_cases(self, detector):
        """Test cases that should not be detected as OWASP questions."""
        assert not detector.is_owasp_question("OWASP is great")
        assert not detector.is_owasp_question("Security is important")

        assert not detector.is_owasp_question("What is Python?")
        assert not detector.is_owasp_question("How do I cook pasta?")

        assert not detector.is_owasp_question("OWASP provides security resources")
        assert not detector.is_owasp_question("Vulnerabilities are common")

    def test_is_owasp_question_empty_or_none(self, detector):
        """Test handling of empty or None input."""
        assert not detector.is_owasp_question("")
        assert not detector.is_owasp_question("   ")
        assert not detector.is_owasp_question(None)

    def test_case_insensitive_detection(self, detector):
        """Test that detection is case insensitive."""
        assert not detector.is_owasp_question("WHAT IS OWASP?")
        assert detector.is_owasp_question("what is owasp?")
        assert not detector.is_owasp_question("What Is OWASP?")
        assert not detector.is_owasp_question("How Do I Fix SECURITY Vulnerabilities?")

    def test_question_with_special_characters(self, detector):
        """Test question detection with special characters."""
        assert detector.is_owasp_question("What is xss & how to prevent it?")
        assert detector.is_owasp_question("Can you explain sql injection (SQLi)?")
        assert detector.is_owasp_question("What's the best owasp tool?")
        assert detector.is_owasp_question("How do I use webgoat 2.0?")

    def test_question_patterns_regex(self, detector):
        """Test individual regex patterns."""
        for pattern in detector.compiled_patterns:
            assert pattern is not None

        question_mark_pattern = detector.compiled_patterns[0]
        assert question_mark_pattern.search("Is this right?") is not None

        question_word_pattern = detector.compiled_patterns[1]
        assert question_word_pattern.search("What is this") is not None
        assert question_word_pattern.search("How does it work") is not None

    def test_owasp_keywords_set(self, detector):
        """Test that OWASP keywords is properly initialized."""
        assert isinstance(detector.owasp_keywords, set)
        assert "owasp" in detector.owasp_keywords
        assert "security" in detector.owasp_keywords
        assert "vulnerability" in detector.owasp_keywords
        assert "xss" in detector.owasp_keywords

    def test_whitespace_handling(self, detector):
        """Test proper handling of whitespace in questions."""
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
    def test_complex_owasp_questions(self, detector, question):
        """Test complex real-world OWASP questions."""
        assert detector.is_owasp_question(question.lower()), f"Failed for: {question}"

    def test_mocked_initialization(self):
        """Test with mocked QuestionDetector initialization."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch("openai.OpenAI") as mock_openai,
            patch("apps.slack.common.question_detector.OWASP_KEYWORDS", {"mocked", "keywords"}),
        ):
            mock_openai.return_value = MagicMock()
            detector = QuestionDetector()

            assert detector.owasp_keywords == {"mocked", "keywords"}
            assert len(detector.compiled_patterns) == 4

    def test_class_constants(self, detector):
        """Test that class constants are properly defined."""
        assert detector.MAX_TOKENS == 50
        assert detector.TEMPERATURE == 0.1
        assert detector.CHAT_MODEL == "gpt-4o"

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
                detector.is_owasp_question_with_openai("What is OWASP?")

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
                detector.is_owasp_question_with_openai("What is OWASP?")

    def test_is_owasp_question_with_openai_success_yes(self):
        """Test OpenAI question detection with YES response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
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
            result = detector.is_owasp_question_with_openai("What is OWASP?")

            assert result is True

    def test_is_owasp_question_with_openai_success_no(self):
        """Test OpenAI question detection with NO response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
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
            result = detector.is_owasp_question_with_openai("What is Python?")

            assert result is False

    def test_is_owasp_question_with_openai_empty_response(self):
        """Test OpenAI question detection with empty response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
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
            result = detector.is_owasp_question_with_openai("What is OWASP?")

            assert result is None

    def test_is_owasp_question_with_openai_none_response(self):
        """Test OpenAI question detection with None response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
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
            result = detector.is_owasp_question_with_openai("What is OWASP?")

            assert result is None

    def test_is_owasp_question_with_openai_unexpected_response(self):
        """Test OpenAI question detection with unexpected response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
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
            result = detector.is_owasp_question_with_openai("What is OWASP?")

            assert result is None

    def test_is_owasp_question_with_openai_api_error(self):
        """Test OpenAI question detection with API error."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
            ),
            patch("openai.OpenAI") as mock_openai,
        ):
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = openai.OpenAIError("API Error")
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question_with_openai("What is OWASP?")

            assert result is None

    def test_is_owasp_question_with_openai_case_insensitive(self):
        """Test OpenAI question detection with case insensitive responses."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
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
            result = detector.is_owasp_question_with_openai("What is OWASP?")

            assert result is True

    def test_is_owasp_question_with_openai_no_in_response(self):
        """Test OpenAI question detection with 'no' in response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
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
            result = detector.is_owasp_question_with_openai("What is Python?")

            assert result is False

    def test_is_owasp_question_openai_override_with_keywords(self):
        """Test that keyword detection overrides OpenAI NO response."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
            ),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.slack.common.question_detector.QuestionDetector.is_owasp_question_with_openai",
                return_value=False,
            ),
        ):
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question("What is OWASP security?")

            assert result is True

    def test_is_owasp_question_openai_override_without_keywords(self):
        """Test that keyword detection does not override OpenAI NO response when no keywords."""
        with (
            patch.dict(os.environ, {"DJANGO_OPEN_AI_SECRET_KEY": "test-key"}),
            patch(
                "apps.slack.common.question_detector.Prompt.get_slack_question_detector_prompt",
                return_value="System prompt with {keywords}",
            ),
            patch("openai.OpenAI") as mock_openai,
            patch(
                "apps.slack.common.question_detector.QuestionDetector.is_owasp_question_with_openai",
                return_value=False,
            ),
        ):
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            detector = QuestionDetector()
            result = detector.is_owasp_question("What is Python programming?")

            assert result is False
