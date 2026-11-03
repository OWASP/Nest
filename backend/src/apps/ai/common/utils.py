"""AI utils."""

import logging
import time
from datetime import UTC, datetime, timedelta

from apps.ai.common.constants import (
    DEFAULT_LAST_REQUEST_OFFSET_SECONDS,
    MIN_REQUEST_INTERVAL_SECONDS,
)
from apps.ai.embeddings.factory import get_embedder
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context

logger: logging.Logger = logging.getLogger(__name__)


def create_chunks_and_embeddings(
    chunk_texts: list[str],
    context: Context,
    *,
    save: bool = True,
) -> list[Chunk]:
    """Create chunks and embeddings from given texts.

    Args:
        chunk_texts (list[str]): List of text chunks to process
        context (Context): The context these chunks belong to
        save (bool): Whether to save chunks immediately

    Returns:
        list[Chunk]: List of created Chunk instances (empty if failed)

    """
    try:
        last_request_time = datetime.now(UTC) - timedelta(
            seconds=DEFAULT_LAST_REQUEST_OFFSET_SECONDS
        )
        time_since_last_request = datetime.now(UTC) - last_request_time

        if time_since_last_request < timedelta(seconds=MIN_REQUEST_INTERVAL_SECONDS):
            time.sleep(MIN_REQUEST_INTERVAL_SECONDS - time_since_last_request.total_seconds())

        try:
            embeddings = get_embedder().embed_documents(chunk_texts)
        except Exception:
            logger.exception("Failed to generate embeddings")
            return []

        chunks = []
        for text, embedding in zip(chunk_texts, embeddings, strict=True):
            chunk = Chunk.update_data(text=text, embedding=embedding, context=context, save=save)
            if chunk is not None:
                chunks.append(chunk)

    except (AttributeError, TypeError):
        logger.exception("Failed to create chunks and embeddings")
        return []
    else:
        return chunks


def extract_json_from_markdown(content: str) -> str:
    """Extract JSON content from markdown code blocks.

    Args:
        content (str): The content string that may contain markdown code blocks

    Returns:
        str: The extracted JSON content with code block markers removed

    """
    if "```json" in content:
        return content.split("```json")[1].split("```", maxsplit=1)[0].strip()
    if "```" in content:
        return content.split("```")[1].split("```", maxsplit=1)[0].strip()
    return content


def get_fallback_response() -> str:
    """Get fallback response on error.

    Returns:
        Fallback error message (detailed in development, generic in production)

    """
    from django.conf import settings  # noqa: PLC0415

    # Only show detailed error message in local/development environment
    if settings.IS_LOCAL_ENVIRONMENT or settings.DEBUG:
        return (
            "⚠️ I encountered an error processing your request. "
            "Please try rephrasing your question or contact support if the issue persists."
        )

    # Generic message for production
    return (
        "I'm sorry, I encountered an issue processing your request. "
        "Please try again or rephrasing your question."
    )


def get_intent_to_agent_map() -> dict:
    """Get intent to agent map.

    Returns:
        Dictionary with intent as key and agent constructor as value.

    """
    from apps.ai.agents.chapter import create_chapter_agent  # noqa: PLC0415
    from apps.ai.agents.community import create_community_agent  # noqa: PLC0415
    from apps.ai.agents.contribution import create_contribution_agent  # noqa: PLC0415
    from apps.ai.agents.project import create_project_agent  # noqa: PLC0415
    from apps.ai.agents.rag import create_rag_agent  # noqa: PLC0415
    from apps.ai.common.intent import Intent  # noqa: PLC0415

    return {
        Intent.CHAPTER.value: create_chapter_agent,
        Intent.COMMUNITY.value: create_community_agent,
        Intent.CONTRIBUTION.value: create_contribution_agent,
        Intent.GSOC.value: create_contribution_agent,  # GSoC queries handled by contribution agent
        Intent.PROJECT.value: create_project_agent,
        Intent.RAG.value: create_rag_agent,
    }


def regenerate_chunks_for_context(context: Context):
    """Regenerates all chunks for a single, specific context instance.

    Args:
      context (Context): The specific context instance to be updated.

    """
    context.chunks.all().delete()
    new_chunk_texts = Chunk.split_text(context.content)

    if not new_chunk_texts:
        logger.warning("No content to chunk for Context. Process stopped.")
        return

    create_chunks_and_embeddings(
        chunk_texts=new_chunk_texts,
        context=context,
        save=True,
    )

    logger.info("Successfully completed chunk regeneration for new context")
