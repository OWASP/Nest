"""Handler for AI-powered Slack functionality."""

from __future__ import annotations

import logging

from apps.ai.agent.agent import AgenticRAGAgent
from apps.slack.blocks import markdown
from apps.slack.common.question_detector import QuestionDetector

logger = logging.getLogger(__name__)


def get_blocks(query: str) -> list[dict]:
    """Get AI response blocks.

    Args:
        query (str): The user's question.
        presentation (EntityPresentation | None): Configuration for entity presentation.

    Returns:
        list: A list of Slack blocks representing the AI response.

    """
    ai_response = process_ai_query(query.strip())

    if ai_response:
        return [markdown(ai_response)]
    return get_error_blocks()


def process_ai_query(query: str) -> str | None:
    """Process the AI query using the agentic RAG agent.

    Args:
        query (str): The user's question.

    Returns:
        str | None: The AI response or None if error occurred.

    """
    question_detector = QuestionDetector()
    if not question_detector.is_owasp_question(text=query):
        return get_default_response()

    agent = AgenticRAGAgent()
    result = agent.run(query=query)
    return result["answer"]


def get_error_blocks() -> list[dict]:
    """Get error response blocks.

    Returns:
        list: A list of Slack blocks with error message.

    """
    return [
        markdown(
            "⚠️ Unfortunately, I'm unable to answer your question at this time.\n"
            "Please try again later or contact support if the issue persists."
        )
    ]


def get_default_response() -> str:
    """Get default response for non-OWASP questions.

    Returns:
        str: A default response for non-OWASP questions.

    """
    return "Please ask questions related to OWASP."
