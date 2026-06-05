"""Semantic cache service for AI query responses."""

from apps.ai.common.crewai_config import CrewAIConfig
from apps.ai.models.semantic_cache import SemanticCache

_config = CrewAIConfig()


def get_cached_response(query: str) -> str | None:
    """Look up semantically similar cached response.

    Args:
        query (str): User query text.

    Returns:
        str: Cached response string if found within similarity threshold and TTL,
        None otherwise.

    """
    if not _config.semantic_cache_enabled:
        return None

    return SemanticCache.get_cached_response(
        query,
        similarity_threshold=_config.semantic_cache_similarity_threshold,
        ttl_seconds=_config.semantic_cache_ttl_seconds,
    )


def store_cached_response(
    query: str,
    response: str,
    intent: str = "",
    confidence: float = 0.0,
) -> SemanticCache | None:
    """Store query-response pair in semantic cache.

    Args:
        query (str): Original query text.
        response (str): Generated response text.
        intent (str): Classified intent for the query.
        confidence (float): Router confidence score.

    Returns:
        Created SemanticCache instance.

    """
    if not _config.semantic_cache_enabled:
        return None

    return SemanticCache.store_response(
        query=query,
        response=response,
        intent=intent,
        confidence=confidence,
    )
