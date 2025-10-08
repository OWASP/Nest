"""Handler for AI-powered Slack functionality."""

from __future__ import annotations

import logging

from apps.ai.agent.tools.rag.rag_tool import RagTool
from apps.slack.blocks import markdown
from apps.slack.constants import CONVERSATION_CONTEXT_LIMIT
from apps.slack.models import Conversation, Workspace

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
    """Process the AI query using the RAG tool.

    Args:
        query (str): The user's question.

    Returns:
        str | None: The AI response or None if error occurred.

    """
    rag_tool = RagTool(
        chat_model="gpt-4o",
        embedding_model="text-embedding-3-small",
    )

    return rag_tool.query(question=query)


def get_dm_blocks(query: str, workspace_id: str, channel_id: str) -> list[dict]:
    """Get AI response blocks for DM with conversation context.

    Args:
        query (str): The user's question.
        workspace_id (str): Slack workspace ID.
        channel_id (str): Slack channel ID for the DM.

    Returns:
        list: A list of Slack blocks representing the AI response.

    """
    ai_response = process_dm_ai_query(query.strip(), workspace_id, channel_id)

    if ai_response:
        return [markdown(ai_response)]
    return get_error_blocks()


def process_dm_ai_query(query: str, workspace_id: str, channel_id: str) -> str | None:
    """Process the AI query with DM conversation context.

    Args:
        query (str): The user's question.
        workspace_id (str): Slack workspace ID.
        channel_id (str): Slack channel ID for the DM.

    Returns:
        str | None: The AI response or None if error occurred.

    """
    workspace = Workspace.objects.get(slack_workspace_id=workspace_id)
    conversation = Conversation.objects.get(slack_channel_id=channel_id, workspace=workspace)

    context = conversation.get_context(conversation_context_limit=CONVERSATION_CONTEXT_LIMIT)

    rag_tool = RagTool(
        chat_model="gpt-4o",
        embedding_model="text-embedding-3-small",
    )

    if context:
        enhanced_query = f"Conversation context:\n{context}\n\nCurrent question: {query}"
    else:
        enhanced_query = query

    response = rag_tool.query(question=enhanced_query)
    conversation.add_to_context(query, response)

    return response


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
