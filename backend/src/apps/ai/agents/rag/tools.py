"""RAG-specific tools for semantic search."""

from typing import Any

from crewai.tools import tool
from pgvector.django.functions import CosineDistance

from apps.ai.embeddings.factory import get_embedder
from apps.ai.models.chunk import Chunk


@tool("Semantic search for OWASP content")
def semantic_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search OWASP content using semantic similarity.

    This tool searches through OWASP content (from www-* repositories)
    using embeddings to find semantically similar content.

    Use this tool when users ask complex questions that require:
    - Context from OWASP documentation
    - Information from OWASP policies
    - Details from OWASP repositories
    - General OWASP knowledge

    Args:
        query: The search query
        limit: Maximum number of results to return (default: 5)

    Returns:
        List of dictionaries with 'text' and 'context' keys containing
        relevant OWASP content chunks

    """
    embedder = get_embedder()
    query_embedding = embedder.embed_query(query)

    # Search pgvector using cosine distance
    chunks = Chunk.objects.annotate(
        distance=CosineDistance("embedding", query_embedding)
    ).order_by("distance")[:limit]

    return [
        {
            "text": chunk.text,
            "context": str(chunk.context) if chunk.context else "Unknown",
            "distance": float(chunk.distance) if hasattr(chunk, "distance") else 0.0,
        }
        for chunk in chunks
    ]
