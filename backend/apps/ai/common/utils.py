"""AI utils."""

import logging
import time
from datetime import UTC, datetime, timedelta

from openai import OpenAI, OpenAIError

from apps.ai.common.constants import (
    DEFAULT_LAST_REQUEST_OFFSET_SECONDS,
    MIN_REQUEST_INTERVAL_SECONDS,
)
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context

logger: logging.Logger = logging.getLogger(__name__)


def create_chunks_and_embeddings(
    chunk_texts: list[str],
    context: Context,
    openai_client,
    model: str = "text-embedding-3-small",
    *,
    save: bool = True,
) -> list[Chunk]:
    """Create chunks and embeddings from given texts using OpenAI embeddings.

    Args:
        chunk_texts (list[str]): List of text chunks to process
        context (Context): The context these chunks belong to
        openai_client: Initialized OpenAI client
        model (str): Embedding model to use
        save (bool): Whether to save chunks immediately

    Returns:
        list[Chunk]: List of created Chunk instances (empty if failed)

    Raises:
        ValueError: If context is None or invalid

    """
    from apps.ai.models.chunk import Chunk

    try:
        last_request_time = datetime.now(UTC) - timedelta(
            seconds=DEFAULT_LAST_REQUEST_OFFSET_SECONDS
        )
        time_since_last_request = datetime.now(UTC) - last_request_time

        if time_since_last_request < timedelta(seconds=MIN_REQUEST_INTERVAL_SECONDS):
            time.sleep(MIN_REQUEST_INTERVAL_SECONDS - time_since_last_request.total_seconds())

        response = openai_client.embeddings.create(
            input=chunk_texts,
            model=model,
        )
        embeddings = [d.embedding for d in response.data]

        chunks = []
        for text, embedding in zip(chunk_texts, embeddings, strict=True):
            chunk = Chunk.update_data(text=text, embedding=embedding, context=context, save=save)
            if chunk is not None:
                chunks.append(chunk)

    except (OpenAIError, AttributeError, TypeError):
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
        return content.split("```json")[1].split("```")[0].strip()
    if "```" in content:
        return content.split("```")[1].split("```")[0].strip()
    return content


def regenerate_chunks_for_context(context: Context):
    """Regenerates all chunks for a single, specific context instance.

    Args:
      context (Context): The specific context instance to be updated.

    """
    from apps.ai.models.chunk import Chunk

    context.chunks.all().delete()
    new_chunk_texts = Chunk.split_text(context.content)

    if not new_chunk_texts:
        logger.warning("No content to chunk for Context. Process stopped.")
        return

    openai_client = OpenAI()

    create_chunks_and_embeddings(
        chunk_texts=new_chunk_texts,
        context=context,
        openai_client=openai_client,
        save=True,
    )

    logger.info("Successfully completed chunk regeneration for new context")
