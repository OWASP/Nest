"""Tests for question detector functionality."""

from unittest.mock import Mock, patch

import pytest

from apps.slack.common.question_detector import QuestionDetector


class TestQuestionDetector:
    """Test cases for QuestionDetector functionality."""

    @pytest.fixture
    def detector(self):
        """Fixture to provide QuestionDetector instance."""
        return QuestionDetector()

    @pytest.fixture
    def mock_detector_dependencies(self):
        """Mock any external dependencies if needed."""
        with patch("apps.slack.common.question_detector.QuestionDetector") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            yield mock_instance

    def test_init(self, detector):
        """Test QuestionDetector initialization."""
        assert detector.owasp_keywords is not None
        assert len(detector.question_patterns) == 4
        assert len(detector.compiled_patterns) == 4

    def test_is_question_with_question_mark(self, detector):
        """Test question detection with question mark."""
        assert detector.is_question("What is OWASP?") is True
        assert detector.is_question("How does security work?") is True
        assert detector.is_question("Is this secure?") is True

    def test_is_question_with_question_words(self, detector):
        """Test question detection with question words."""
        assert detector.is_question("What is security") is True
        assert detector.is_question("How can I help") is True
        assert detector.is_question("Why does this happen") is True
        assert detector.is_question("When should I use this") is True
        assert detector.is_question("Where can I find documentation") is True
        assert detector.is_question("Which tool is better") is True
        assert detector.is_question("Who can help me") is True
        assert detector.is_question("Can you explain") is True
        assert detector.is_question("Could this work") is True
        assert detector.is_question("Would you recommend") is True
        assert detector.is_question("Should I use this") is True
        assert detector.is_question("Is this correct") is True
        assert detector.is_question("Are there alternatives") is True
        assert detector.is_question("Does this work") is True
        assert detector.is_question("Do you know") is True
        assert detector.is_question("Did this happen") is True

    def test_is_question_with_help_words(self, detector):
        """Test question detection with help-related words."""
        assert detector.is_question("Please help me with security") is True
        assert detector.is_question("Can you explain this concept") is True
        assert detector.is_question("Tell me about OWASP") is True
        assert detector.is_question("Show me an example") is True
        assert detector.is_question("I need a guide") is True
        assert detector.is_question("Looking for a tutorial") is True

    def test_is_question_with_advice_words(self, detector):
        """Test question detection with advice-related words."""
        assert detector.is_question("I recommend this approach") is True
        assert detector.is_question("Can you suggest something") is True
        assert detector.is_question("What's your advice") is True
        assert detector.is_question("Need your opinion") is True

    def test_is_question_false_cases(self, detector):
        """Test cases that should not be detected as questions."""
        assert detector.is_question("This is a statement") is False
        assert detector.is_question("OWASP is great") is False
        assert detector.is_question("Security vulnerabilities exist") is False
        assert detector.is_question("Hello everyone") is False
        assert detector.is_question("Thanks for your assistance") is False

    def test_contains_owasp_keywords_single_words(self, detector):
        """Test OWASP keyword detection with single words."""
        assert detector.contains_owasp_keywords("owasp security") is True
        assert detector.contains_owasp_keywords("vulnerability assessment") is True
        assert detector.contains_owasp_keywords("zap tool") is True
        assert detector.contains_owasp_keywords("appsec testing") is True
        assert detector.contains_owasp_keywords("devsecops pipeline") is True
        assert detector.contains_owasp_keywords("xss attack") is True
        assert detector.contains_owasp_keywords("csrf protection") is True
        assert detector.contains_owasp_keywords("injection prevention") is True

    def test_contains_owasp_keywords_multi_word_phrases(self, detector):
        """Test OWASP keyword detection with multi-word phrases."""
        assert detector.contains_owasp_keywords("threat modeling process") is True
        assert detector.contains_owasp_keywords("defect dojo tool") is True
        assert detector.contains_owasp_keywords("juice shop example") is True
        assert detector.contains_owasp_keywords("red team exercise") is True
        assert detector.contains_owasp_keywords("application security testing") is True
        assert detector.contains_owasp_keywords("web security best practices") is True
        assert detector.contains_owasp_keywords("mobile security guidelines") is True
        assert detector.contains_owasp_keywords("api security framework") is True

    def test_contains_owasp_keywords_false_cases(self, detector):
        """Test cases that should not contain OWASP keywords."""
        assert detector.contains_owasp_keywords("hello world") is False
        assert detector.contains_owasp_keywords("python programming") is False
        assert detector.contains_owasp_keywords("weather forecast") is False
        assert detector.contains_owasp_keywords("random conversation") is False

    def test_is_owasp_question_true_cases(self, detector):
        """Test cases that should be detected as OWASP questions."""
        assert detector.is_owasp_question("What is OWASP?") is True
        assert detector.is_owasp_question("How do I fix security vulnerabilities?") is True
        assert detector.is_owasp_question("Can you explain XSS attacks?") is True
        assert detector.is_owasp_question("What are the OWASP Top 10?") is True
        assert detector.is_owasp_question("How does ZAP work?") is True
        assert detector.is_owasp_question("Tell me about application security") is True
        assert detector.is_owasp_question("I need help with threat modeling") is True
        assert detector.is_owasp_question("Can you recommend secure coding practices?") is True

    def test_is_owasp_question_false_cases(self, detector):
        """Test cases that should not be detected as OWASP questions."""
        assert detector.is_owasp_question("OWASP is great") is False
        assert detector.is_owasp_question("Security is important") is False

        assert detector.is_owasp_question("What is Python?") is False
        assert detector.is_owasp_question("How do I cook pasta?") is False

        assert detector.is_owasp_question("OWASP provides security resources") is False
        assert detector.is_owasp_question("Vulnerabilities are common") is False

    def test_is_owasp_question_empty_or_none(self, detector):
        """Test handling of empty or None input."""
        assert detector.is_owasp_question("") is False
        assert detector.is_owasp_question("   ") is False
        assert detector.is_owasp_question(None) is False

    def test_case_insensitive_detection(self, detector):
        """Test that detection is case insensitive."""
        assert detector.is_owasp_question("WHAT IS OWASP?") is True
        assert detector.is_owasp_question("what is owasp?") is True
        assert detector.is_owasp_question("What Is OWASP?") is True
        assert detector.is_owasp_question("How Do I Fix SECURITY Vulnerabilities?") is True

    def test_question_with_special_characters(self, detector):
        """Test question detection with special characters."""
        assert detector.is_owasp_question("What is XSS & how to prevent it?") is True
        assert detector.is_owasp_question("Can you explain SQL injection (SQLi)?") is True
        assert detector.is_owasp_question("What's the best OWASP tool?") is True
        assert detector.is_owasp_question("How do I use ZAP 2.0?") is True

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
        assert detector.is_owasp_question("  What is OWASP?  ") is True
        assert detector.is_owasp_question("\tHow does security work?\n") is True
        assert detector.is_owasp_question("What\nis\nOWASP?") is True

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
        assert detector.is_owasp_question(question) is True, f"Failed for: {question}"

    def test_mocked_initialization(self):
        """Test with mocked QuestionDetector initialization."""
        with patch("apps.slack.common.question_detector.OWASP_KEYWORDS", {"mocked", "keywords"}):
            detector = QuestionDetector()

            assert detector.owasp_keywords == {"mocked", "keywords"}
            assert len(detector.question_patterns) == 4
            assert len(detector.compiled_patterns) == 4
