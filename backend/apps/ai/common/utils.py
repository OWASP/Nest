"""AI utils."""

import logging
import time
from datetime import UTC, datetime, timedelta

import openai
from django.contrib.contenttypes.models import ContentType

from apps.ai.common.constants import (
    DEFAULT_LAST_REQUEST_OFFSET_SECONDS,
    MIN_REQUEST_INTERVAL_SECONDS,
)
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context

logger: logging.Logger = logging.getLogger(__name__)


def create_context(content: str, content_object=None, source: str = "") -> Context:
    """Create and save a Context instance independently.

    Args:
        content (str): The context content
        content_object: Optional related object
        source (str): Source identifier

    Returns:
        Context: Created Context instance

    """
    context = Context.update_data(content=content, content_object=content_object, source=source)
    if context is None:
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            context = Context.objects.get(
                content_type=content_type, object_id=content_object.pk, content=content
            )
        else:
            context = Context.objects.get(content=content, content_object__isnull=True)

    return context


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

    """
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
            chunk = Chunk.update_data(text=text, context=context, embedding=embedding, save=save)
            if chunk:
                chunks.append(chunk)

    except openai.OpenAIError:
        logger.exception("Failed to create chunks and embeddings")
        return []
    else:
        return chunks
