"""Question detection utilities for Slack OWASP bot."""

from __future__ import annotations

import logging
import os
import re

import openai
from django.core.exceptions import ObjectDoesNotExist

from apps.core.models.prompt import Prompt
from apps.slack.constants import OWASP_KEYWORDS

logger = logging.getLogger(__name__)


class QuestionDetector:
    """Utility class for detecting OWASP-related questions."""

    MAX_TOKENS = 50
    TEMPERATURE = 0.1
    CHAT_MODEL = "gpt-4o"

    def __init__(self):
        """Initialize the question detector.

        Raises:
            ValueError: If the OpenAI API key is not set.

        """
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            error_msg = "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            raise ValueError(error_msg)

        self.owasp_keywords = OWASP_KEYWORDS
        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        question_patterns = [
            r"\?",
            r"^(what|how|why|when|where|which|who|can|could|would|should|is|are|does|do|did)",
            r"(help|explain|tell me|show me|guide|tutorial|example)",
            r"(recommend|suggest|advice|opinion)",
        ]

        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in question_patterns
        ]

    def is_owasp_question(self, text: str) -> bool:
        """Check if the input text is an OWASP-related question.

        This is the main public method that orchestrates the detection logic.
        """
        if not text or not text.strip():
            return False

        if not self.is_question(text):
            return False

        openai_result = self.is_owasp_question_with_openai(text)

        if openai_result is None:
            logger.warning(
                "OpenAI detection failed. Falling back to keyword matching",
            )
            return self.contains_owasp_keywords(text)

        if openai_result:
            return True
        if self.contains_owasp_keywords(text):
            logger.info(
                "OpenAI classified as non-OWASP, but keywords were detected. Overriding to TRUE."
            )
            return True
        return False

    def is_question(self, text: str) -> bool:
        """Check if text appears to be a question."""
        return any(pattern.search(text) for pattern in self.compiled_patterns)

    def is_owasp_question_with_openai(self, text: str) -> bool | None:
        """Determine if the text is an OWASP-related question.

        Returns:
            - True: If the model responds with "YES".
            - False: If the model responds with "NO".
            - None: If the API call fails or the response is unexpected.

        """
        prompt_template = Prompt.get_slack_question_detector_prompt()
        if not prompt_template or not prompt_template.strip():
            error_msg = "Prompt with key 'slack-question-detector-system-prompt' not found."
            raise ObjectDoesNotExist(error_msg)

        system_prompt = prompt_template.format(keywords=", ".join(self.owasp_keywords))
        user_prompt = f'Question: "{text}"'

        try:
            response = self.openai_client.chat.completions.create(
                model=self.CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )
        except openai.OpenAIError:
            logger.exception("OpenAI API error during question detection")
            return None
        else:
            answer = response.choices[0].message.content
            if not answer:
                logger.error("OpenAI returned an empty response")
                return None

            clean_answer = answer.strip().upper()

            if "YES" in clean_answer:
                return True
            if "NO" in clean_answer:
                return False
            logger.warning("Unexpected OpenAI response")
            return None

    def contains_owasp_keywords(self, text: str) -> bool:
        """Check if text contains OWASP-related keywords."""
        words = re.findall(r"\b\w+\b", text)
        text_words = set(words)

        intersection = self.owasp_keywords.intersection(text_words)
        if intersection:
            return True

        return any(" " in keyword and keyword in text for keyword in self.owasp_keywords)
