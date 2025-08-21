"""Question detection utilities for Slack OWASP bot."""

from __future__ import annotations

import logging
import re

from apps.slack.constants import OWASP_KEYWORDS

logger = logging.getLogger(__name__)


class QuestionDetector:
    """Utility class for detecting OWASP-related questions."""

    def __init__(self):
        """Initialize the question detector."""
        self.owasp_keywords = OWASP_KEYWORDS

        self.question_patterns = [
            r"\?",
            r"^(what|how|why|when|where|which|who|can|could|would|should|is|are|does|do|did)",
            r"(help|explain|tell me|show me|guide|tutorial|example)",
            r"(recommend|suggest|advice|opinion)",
        ]

        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.question_patterns
        ]

    def is_owasp_question(self, text: str) -> bool:
        """Check if text contains an OWASP-related question."""
        if not text or not text.strip():
            return False

        text_lower = text.lower().strip()

        is_a_question = self.is_question(text_lower)
        if not is_a_question:
            return False

        return self.contains_owasp_keywords(text_lower)

    def is_question(self, text: str) -> bool:
        """Check if text appears to be a question."""
        return any(pattern.search(text) for pattern in self.compiled_patterns)

    def contains_owasp_keywords(self, text: str) -> bool:
        """Check if text contains OWASP-related keywords."""
        words = re.findall(r"\b\w+\b", text)
        text_words = set(words)

        intersection = self.owasp_keywords.intersection(text_words)
        if intersection:
            return True

        return any(" " in keyword and keyword in text for keyword in self.owasp_keywords)
