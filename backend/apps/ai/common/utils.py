"""AI utils."""

import logging
import time
from datetime import UTC, datetime, timedelta

import openai

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
    try:
        last_request_time = datetime.now(UTC) - timedelta(
            seconds=DEFAULT_LAST_REQUEST_OFFSET_SECONDS
        )
        time_since_last_request = datetime.now(UTC) - last_request_time

        if time_since_last_request < timedelta(seconds=MIN_REQUEST_INTERVAL_SECONDS):
            time.sleep(
                MIN_REQUEST_INTERVAL_SECONDS - time_since_last_request.total_seconds()
            )

        response = openai_client.embeddings.create(
            input=chunk_texts,
            model=model,
        )
        embeddings = [d.embedding for d in response.data]

        chunks = []
        for text, embedding in zip(chunk_texts, embeddings, strict=True):
            chunk = Chunk.update_data(
                text=text, embedding=embedding, context=context, save=save
            )
            chunks.append(chunk)

    except ValueError:
        logger.exception("Context error")
        raise
    except openai.OpenAIError:
        logger.exception("Failed to create chunks and embeddings")
        return []
    else:
        return chunks
