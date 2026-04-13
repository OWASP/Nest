"""AI app semantic cache model."""

import logging
from datetime import UTC, datetime, timedelta

from django.db import models
from pgvector.django import VectorField
from pgvector.django.functions import CosineDistance

from apps.ai.models.chunk import EMBEDDING_DIMENSIONS
from apps.common.models import TimestampedModel
from apps.common.utils import truncate

logger = logging.getLogger(__name__)


class SemanticCache(TimestampedModel):
    """Semantic cache model for storing query-response pairs with embeddings."""

    class Meta:
        """Model options."""

        db_table = "ai_semantic_cache"
        verbose_name = "Semantic Cache"

    confidence = models.FloatField(verbose_name="Confidence", default=0.0)
    intent = models.CharField(verbose_name="Intent", blank=True, default="", max_length=50)
    query_embedding = VectorField(verbose_name="Query Embedding", dimensions=EMBEDDING_DIMENSIONS)
    query_text = models.TextField(verbose_name="Query Text")
    response_text = models.TextField(verbose_name="Response Text")

    def __str__(self):
        """Human readable representation."""
        return f"SemanticCache {self.id}: {truncate(self.query_text, 50)}"

    @staticmethod
    def get_cached_response(
        query: str,
        *,
        similarity_threshold: float = 0.95,
        ttl_seconds: int = 86400,
    ) -> str | None:
        """Look up semantically similar cached response.

        Args:
            query: User query text.
            similarity_threshold: Minimum cosine similarity (0.0-1.0).
            ttl_seconds: Maximum age of cached entries in seconds.

        Returns:
            Cached response string if found, None otherwise.

        """
        from apps.ai.embeddings.factory import get_embedder  # noqa: PLC0415

        ttl_cutoff = datetime.now(UTC) - timedelta(seconds=ttl_seconds)
        max_distance = 1.0 - similarity_threshold

        result = (
            SemanticCache.objects.filter(nest_created_at__gte=ttl_cutoff)
            .annotate(
                distance=CosineDistance("query_embedding", get_embedder().embed_query(query))
            )
            .filter(distance__lte=max_distance)
            .order_by("distance")
            .first()
        )

        if result is not None:
            logger.info(
                "Semantic cache hit",
                extra={
                    "cache_id": result.id,
                    "distance": float(result.distance),
                    "query_preview": query[:100],
                },
            )
            return result.response_text

        return None

    @staticmethod
    def store_response(
        query: str,
        response: str,
        intent: str = "",
        confidence: float = 0.0,
    ) -> "SemanticCache":
        """Store query-response pair in semantic cache.

        Args:
            query: Original query text.
            response: Generated response text.
            intent: Classified intent for the query.
            confidence: Router confidence score.

        Returns:
            Created SemanticCache instance.

        """
        from apps.ai.embeddings.factory import get_embedder  # noqa: PLC0415

        entry = SemanticCache(
            query_text=query,
            query_embedding=get_embedder().embed_query(query),
            response_text=response,
            intent=intent,
            confidence=confidence,
        )
        entry.save()

        logger.info(
            "Semantic cache stored",
            extra={
                "cache_id": entry.id,
                "intent": intent,
                "query_preview": query[:100],
            },
        )
        return entry
