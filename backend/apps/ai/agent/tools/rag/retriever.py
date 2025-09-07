"""Context retriever for RAG."""

import logging
import os
import re
from typing import Any

import openai
from django.db.models import Q
from pgvector.django.functions import CosineDistance

from apps.ai.common.constants import (
    DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
    DEFAULT_SIMILARITY_THRESHOLD,
)
from apps.ai.models.chunk import Chunk

logger = logging.getLogger(__name__)


class Retriever:
    """A class for retrieving relevant text chunks for a RAG."""

    SUPPORTED_ENTITY_TYPES = (
        "chapter",
        "committee",
        "event",
        "message",
        "project",
    )

    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        """Initialize the Retriever.

        Args:
            embedding_model (str, optional): The OpenAI embedding model to use.

        Raises:
            ValueError: If the OpenAI API key is not set.

        """
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            error_msg = "DJANGO_OPEN_AI_SECRET_KEY environment variable not set"
            raise ValueError(error_msg)
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model
        logger.info("Retriever initialized with embedding model: %s", self.embedding_model)

    def get_query_embedding(self, query: str) -> list[float]:
        """Generate embedding for the user query.

        Args:
            query: The query text.

        Returns:
            A list of floats representing the query embedding.

        """
        try:
            response = self.openai_client.embeddings.create(
                input=[query],
                model=self.embedding_model,
            )
            return response.data[0].embedding
        except openai.OpenAIError:
            logger.exception("OpenAI API error")
            raise
        except Exception:
            logger.exception("Unexpected error while generating embedding")
            raise

    def get_source_name(self, entity) -> str:
        """Get the name/identifier for the content object."""
        for attr in ("name", "title", "login", "key", "summary"):
            if getattr(entity, attr, None):
                return str(getattr(entity, attr))
        return str(entity)

    def get_additional_context(self, entity) -> dict[str, Any]:
        """Get additional context information based on content type.

        Args:
            entity: The source object.

        Returns:
            A dictionary with additional context information.

        """
        context = {}
        clean_content_type = entity.__class__.__name__.lower()
        if clean_content_type == "chapter":
            context.update(
                {
                    "location": getattr(entity, "suggested_location", None),
                    "region": getattr(entity, "region", None),
                    "country": getattr(entity, "country", None),
                    "postal_code": getattr(entity, "postal_code", None),
                    "currency": getattr(entity, "currency", None),
                    "meetup_group": getattr(entity, "meetup_group", None),
                    "tags": getattr(entity, "tags", []),
                    "topics": getattr(entity, "topics", []),
                    "leaders": getattr(entity, "leaders_raw", []),
                    "related_urls": getattr(entity, "related_urls", []),
                    "is_active": getattr(entity, "is_active", None),
                    "url": getattr(entity, "url", None),
                }
            )
        elif clean_content_type == "project":
            context.update(
                {
                    "level": getattr(entity, "level", None),
                    "project_type": getattr(entity, "type", None),
                    "languages": getattr(entity, "languages", []),
                    "topics": getattr(entity, "topics", []),
                    "licenses": getattr(entity, "licenses", []),
                    "tags": getattr(entity, "tags", []),
                    "custom_tags": getattr(entity, "custom_tags", []),
                    "stars_count": getattr(entity, "stars_count", None),
                    "forks_count": getattr(entity, "forks_count", None),
                    "contributors_count": getattr(entity, "contributors_count", None),
                    "releases_count": getattr(entity, "releases_count", None),
                    "open_issues_count": getattr(entity, "open_issues_count", None),
                    "leaders": getattr(entity, "leaders_raw", []),
                    "related_urls": getattr(entity, "related_urls", []),
                    "created_at": getattr(entity, "created_at", None),
                    "updated_at": getattr(entity, "updated_at", None),
                    "released_at": getattr(entity, "released_at", None),
                    "health_score": getattr(entity, "health_score", None),
                    "is_active": getattr(entity, "is_active", None),
                    "track_issues": getattr(entity, "track_issues", None),
                    "url": getattr(entity, "url", None),
                }
            )
        elif clean_content_type == "event":
            context.update(
                {
                    "start_date": getattr(entity, "start_date", None),
                    "end_date": getattr(entity, "end_date", None),
                    "location": getattr(entity, "suggested_location", None),
                    "category": getattr(entity, "category", None),
                    "latitude": getattr(entity, "latitude", None),
                    "longitude": getattr(entity, "longitude", None),
                    "url": getattr(entity, "url", None),
                    "description": getattr(entity, "description", None),
                    "summary": getattr(entity, "summary", None),
                }
            )
        elif clean_content_type == "committee":
            context.update(
                {
                    "is_active": getattr(entity, "is_active", None),
                    "leaders": getattr(entity, "leaders", []),
                    "url": getattr(entity, "url", None),
                    "description": getattr(entity, "description", None),
                    "summary": getattr(entity, "summary", None),
                    "tags": getattr(entity, "tags", []),
                    "topics": getattr(entity, "topics", []),
                    "related_urls": getattr(entity, "related_urls", []),
                }
            )
        elif clean_content_type == "message":
            context.update(
                {
                    "channel": (
                        getattr(entity.conversation, "slack_channel_id", None)
                        if hasattr(entity, "conversation") and entity.conversation
                        else None
                    ),
                    "thread_ts": (
                        getattr(entity.parent_message, "ts", None)
                        if hasattr(entity, "parent_message") and entity.parent_message
                        else None
                    ),
                    "ts": getattr(entity, "ts", None),
                    "user": (
                        getattr(entity.author, "name", None)
                        if hasattr(entity, "author") and entity.author
                        else None
                    ),
                }
            )
        return {k: v for k, v in context.items() if v is not None}

    def retrieve(
        self,
        query: str,
        limit: int = DEFAULT_CHUNKS_RETRIEVAL_LIMIT,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        content_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve the most relevant chunks based on vector similarity.

        Args:
            query: The user's query text.
            limit: The maximum number of chunks to retrieve.
            similarity_threshold: The minimum similarity score (0-1).
            content_types: An optional list of content types to filter by.

        Returns:
            A list of dictionaries, each containing chunk text and rich metadata.

        """
        query_embedding = self.get_query_embedding(query)
        if not content_types:
            content_types = self.extract_content_types_from_query(query)
        queryset = Chunk.objects.annotate(
            similarity=1 - CosineDistance("embedding", query_embedding)
        ).filter(similarity__gte=similarity_threshold)
        if content_types:
            content_type_query = Q()
            for name in content_types:
                lower_name = name.lower()
                if "." in lower_name:
                    app_label, model = lower_name.split(".", 1)
                    content_type_query |= Q(
                        context__entity_type__app_label=app_label,
                        context__entity_type__model=model,
                    )
                else:
                    content_type_query |= Q(context__entity_type__model=lower_name)
            queryset = queryset.filter(content_type_query)

        chunks = queryset.select_related("context__entity_type").order_by("-similarity")[:limit]

        results = []
        for chunk in chunks:
            if not chunk.context or not chunk.context.entity:
                logger.warning("Content object is None for chunk %s. Skipping.", chunk.id)
                continue

            source_name = self.get_source_name(chunk.context.entity)
            additional_context = self.get_additional_context(chunk.context.entity)

            results.append(
                {
                    "text": chunk.text,
                    "similarity": float(chunk.similarity),
                    "source_type": chunk.context.entity_type.model,
                    "source_name": source_name,
                    "source_id": chunk.context.entity_id,
                    "additional_context": additional_context,
                }
            )

        return results

    def extract_content_types_from_query(self, query: str) -> list[str]:
        """Scan the query for keywords matching supported content types.

        Args:
            query: The user's query text.

        Returns:
            A list of detected content type names.

        """
        query_words = set(re.findall(r"\b\w+\b", query.lower()))

        detected_types = [
            entity_type
            for entity_type in self.SUPPORTED_ENTITY_TYPES
            if entity_type in query_words or f"{entity_type}s" in query_words
        ]

        if detected_types:
            logger.info("Detected content type keywords in query: %s", detected_types)

        return detected_types
