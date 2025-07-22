"""Context retriever for RAG."""

import logging
import os
import re
from typing import Any

import openai
from django.db.models import Q
from pgvector.django.functions import CosineDistance

from apps.ai.common.constants import DEFAULT_LIMIT, DEFAULT_SIMILARITY_THRESHOLD
from apps.ai.models.chunk import Chunk

logger = logging.getLogger(__name__)


class Retriever:
    """A class for retrieving relevant text chunks for a RAG."""

    SUPPORTED_CONTENT_TYPES = ["event", "project", "chapter", "committee", "message"]

    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        """Initialize the Retriever.

        Args:
            embedding_model (str, optional): The OpenAI embedding model to use".

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
        except openai.error.OpenAIError:
            logger.exception("OpenAI API error")
            raise
        except Exception:
            logger.exception("Unexpected error while generating embedding")
            raise

    def get_source_name(self, content_object) -> str:
        """Get the name/identifier for the content object."""
        for attr in ["name", "title", "login", "key", "summary"]:
            if hasattr(content_object, attr) and getattr(content_object, attr):
                return str(getattr(content_object, attr))

        return str(content_object)

    def get_additional_context(self, content_object, content_type: str) -> dict[str, Any]:
        """Get additional context information based on content type.

        Args:
            content_object: The source object.
            content_type: The model name of the content object.

        Returns:
            A dictionary with additional context information.

        """
        context = {}
        clean_content_type = content_type.split(".")[-1] if "." in content_type else content_type

        if clean_content_type == "chapter":
            context.update(
                {
                    "location": getattr(content_object, "suggested_location", None),
                    "region": getattr(content_object, "region", None),
                    "country": getattr(content_object, "country", None),
                    "postal_code": getattr(content_object, "postal_code", None),
                    "currency": getattr(content_object, "currency", None),
                    "meetup_group": getattr(content_object, "meetup_group", None),
                    "tags": getattr(content_object, "tags", []),
                    "topics": getattr(content_object, "topics", []),
                    "leaders": getattr(content_object, "leaders_raw", []),
                    "related_urls": getattr(content_object, "related_urls", []),
                    "is_active": getattr(content_object, "is_active", None),
                    "url": getattr(content_object, "url", None),
                }
            )
        elif clean_content_type == "project":
            context.update(
                {
                    "level": getattr(content_object, "level", None),
                    "project_type": getattr(content_object, "type", None),
                    "languages": getattr(content_object, "languages", []),
                    "topics": getattr(content_object, "topics", []),
                    "licenses": getattr(content_object, "licenses", []),
                    "tags": getattr(content_object, "tags", []),
                    "custom_tags": getattr(content_object, "custom_tags", []),
                    "stars_count": getattr(content_object, "stars_count", None),
                    "forks_count": getattr(content_object, "forks_count", None),
                    "contributors_count": getattr(content_object, "contributors_count", None),
                    "releases_count": getattr(content_object, "releases_count", None),
                    "open_issues_count": getattr(content_object, "open_issues_count", None),
                    "leaders": getattr(content_object, "leaders_raw", []),
                    "related_urls": getattr(content_object, "related_urls", []),
                    "created_at": getattr(content_object, "created_at", None),
                    "updated_at": getattr(content_object, "updated_at", None),
                    "released_at": getattr(content_object, "released_at", None),
                    "health_score": getattr(content_object, "health_score", None),
                    "is_active": getattr(content_object, "is_active", None),
                    "track_issues": getattr(content_object, "track_issues", None),
                    "url": getattr(content_object, "url", None),
                }
            )
        elif clean_content_type == "event":
            context.update(
                {
                    "start_date": getattr(content_object, "start_date", None),
                    "end_date": getattr(content_object, "end_date", None),
                    "location": getattr(content_object, "suggested_location", None),
                    "category": getattr(content_object, "category", None),
                    "latitude": getattr(content_object, "latitude", None),
                    "longitude": getattr(content_object, "longitude", None),
                    "url": getattr(content_object, "url", None),
                    "description": getattr(content_object, "description", None),
                    "summary": getattr(content_object, "summary", None),
                }
            )
        elif clean_content_type == "committee":
            context.update(
                {
                    "is_active": getattr(content_object, "is_active", None),
                    "leaders": getattr(content_object, "leaders", []),
                    "url": getattr(content_object, "url", None),
                    "description": getattr(content_object, "description", None),
                    "summary": getattr(content_object, "summary", None),
                    "tags": getattr(content_object, "tags", []),
                    "topics": getattr(content_object, "topics", []),
                    "related_urls": getattr(content_object, "related_urls", []),
                }
            )
        elif clean_content_type == "message":
            context.update(
                {
                    "channel": getattr(content_object.conversation, "slack_channel_id", None),
                    "thread_ts": getattr(content_object.parent_message, "ts", None),
                    "ts": getattr(content_object, "ts", None),
                    "user": getattr(content_object.author, "name", None),
                    "text": getattr(content_object, "text", None),
                    "attachments": getattr(content_object.raw_data, "attachments", []),
                    "url": getattr(content_object, "url", None),
                }
            )

        return {k: v for k, v in context.items() if v is not None}

    def retrieve(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
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

        final_content_types = content_types
        if not final_content_types:
            final_content_types = self.extract_content_types_from_query(query)

        queryset = Chunk.objects.annotate(
            similarity=1 - CosineDistance("embedding", query_embedding)
        ).filter(similarity__gte=similarity_threshold)

        if final_content_types:
            content_type_query = Q()
            for name in final_content_types:
                lower_name = name.lower()
                if "." in lower_name:
                    app_label, model = lower_name.split(".", 1)
                    content_type_query |= Q(
                        content_type__app_label=app_label, content_type__model=model
                    )
                else:
                    content_type_query |= Q(content_type__model=lower_name)
            queryset = queryset.filter(content_type_query)

        chunks = (
            queryset.select_related("content_type")
            .prefetch_related("content_object")
            .order_by("-similarity")[:limit]
        )

        results = []
        for chunk in chunks:
            if not chunk.content_object:
                logger.warning("Content object is None for chunk %s. Skipping.", chunk.id)
                continue

            source_name = self.get_source_name(chunk.content_object)
            additional_context = self.get_additional_context(
                chunk.content_object, chunk.content_type.model
            )

            results.append(
                {
                    "text": chunk.text,
                    "similarity": float(chunk.similarity),
                    "source_type": chunk.content_type.model,
                    "source_name": source_name,
                    "source_id": chunk.object_id,
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
        detected_types = []
        query_words = set(re.findall(r"\b\w+\b", query.lower()))

        detected_types = [
            content_type
            for content_type in self.SUPPORTED_CONTENT_TYPES
            if content_type in query_words or f"{content_type}s" in query_words
        ]

        if detected_types:
            logger.info("Detected content type keywords in query: %s", detected_types)

        return detected_types
