"""AI utils."""

import logging
import time
from datetime import UTC, datetime, timedelta

from apps.ai.common.constants import (
    DEFAULT_LAST_REQUEST_OFFSET_SECONDS,
    MIN_REQUEST_INTERVAL_SECONDS,
)
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context

logger: logging.Logger = logging.getLogger(__name__)


def create_chunks_and_embeddings(
    all_chunk_texts: list[str],
    content_object,
    openai_client,
) -> list[Chunk]:
    """Create chunks and embeddings from given texts using OpenAI embeddings.

    Args:
      all_chunk_texts (list[str]): List of text chunks to embed.
      content_object: The object to associate the chunks with.
      openai_client: Initialized OpenAI client instance.

    Returns:
      list[Chunk]: List of Chunk instances (not saved).

    """
    try:
        last_request_time = datetime.now(UTC) - timedelta(
            seconds=DEFAULT_LAST_REQUEST_OFFSET_SECONDS
        )
        time_since_last_request = datetime.now(UTC) - last_request_time

        if time_since_last_request < timedelta(seconds=MIN_REQUEST_INTERVAL_SECONDS):
            time.sleep(MIN_REQUEST_INTERVAL_SECONDS - time_since_last_request.total_seconds())

        response = openai_client.embeddings.create(
            input=all_chunk_texts,
            model="text-embedding-3-small",
        )

        context = Context(
            content="\n".join(all_chunk_texts),
            content_object=content_object,
        )
        context.save()

        return [
            chunk
            for text, embedding in zip(
                all_chunk_texts,
                [d.embedding for d in response.data],
                strict=True,
            )
            if (
                chunk := Chunk.update_data(
                    text=text,
                    context=context,
                    embedding=embedding,
                    save=False,
                )
            )
        ]
    except Exception:
        logger.exception("OpenAI API error")
        return []
