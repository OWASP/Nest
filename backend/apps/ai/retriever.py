"""Hybrid retrieval utilities for combining search results.

Implements Reciprocal Rank Fusion (RRF) to merge vector and keyword
search results into a single ranked list.
"""

from __future__ import annotations

from typing import Any

# Fixed constants per project requirements
RRF_K = 60  # Smoothing constant for RRF formula


def weighted_reciprocal_rank(
    vector_results: list[dict[str, Any]],
    bm25_results: list[dict[str, Any]],
    *,
    k: int = RRF_K,
    id_key: str = "source_id",
) -> list[dict[str, Any]]:
    """Merge two ranked lists using Reciprocal Rank Fusion.

    RRF assigns scores based on rank position rather than raw scores,
    making it robust to score distribution differences between systems.

    Formula: rrf_score = sum(1 / (k + rank)) across all lists

    Args:
        vector_results: Results from vector/semantic search, best first.
        bm25_results: Results from BM25/keyword search, best first.
        k: Smoothing constant. Higher k reduces impact of top ranks.
        id_key: Field used to identify unique documents.

    Returns:
        Merged list sorted by combined RRF score, highest first.
        Each result gets an 'rrf_score' field added.

    Raises:
        ValueError: If k is not a positive number (must be > 0).
        ValueError: If any document in vector_results or bm25_results
            is missing the specified id_key field.

    """
    # Validate k parameter to prevent division-by-zero or nonsensical scores
    if not isinstance(k, (int, float)) or k <= 0:
        msg = f"k must be a positive number, got {k!r}"
        raise ValueError(msg)

    scores: dict[str, float] = {}
    docs: dict[str, dict[str, Any]] = {}

    # Score by rank position in vector results
    for rank, doc in enumerate(vector_results, start=1):
        if id_key not in doc:
            msg = f"Document missing required '{id_key}' field"
            raise ValueError(msg)
        doc_id = str(doc[id_key])
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
        if doc_id not in docs:
            docs[doc_id] = doc

    # Score by rank position in BM25 results
    for rank, doc in enumerate(bm25_results, start=1):
        if id_key not in doc:
            msg = f"Document missing required '{id_key}' field"
            raise ValueError(msg)
        doc_id = str(doc[id_key])
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
        if doc_id not in docs:
            docs[doc_id] = doc

    # Build output sorted by score
    ranked_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    output = []
    for doc_id in ranked_ids:
        merged = docs[doc_id].copy()
        merged["rrf_score"] = scores[doc_id]
        output.append(merged)

    return output


class HybridRetriever:
    """Combines vector semantic search with keyword BM25 search."""

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Perform hybrid search.

        Args:
            query: Search query string.
            limit: Number of results to return.

        Returns:
            List of ranked results with 'rrf_score'.

        """
        # Fetch more candidates for RRF re-ranking
        candidate_limit = limit * 2

        # Parallel execution would be ideal here, but sequential for now
        vector_res = self._vector_search(query, candidate_limit)
        keyword_res = self._keyword_search(query, candidate_limit)

        return weighted_reciprocal_rank(vector_res, keyword_res)[:limit]

    def _vector_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        """Run semantic vector search using pgvector."""
        import os

        import openai

        from apps.ai.models.chunk import Chunk

        api_key = os.getenv("DJANGO_OPEN_AI_SECRET_KEY")
        if not api_key:
            # Fail gracefully or log warning, but for now raise to signal config error
            msg = "DJANGO_OPEN_AI_SECRET_KEY not set"
            raise ValueError(msg)

        client = openai.OpenAI(api_key=api_key)
        # embedding model should also be configurable, usually text-embedding-ada-002 or 3-small
        resp = client.embeddings.create(input=query, model="text-embedding-3-small")
        embedding = resp.data[0].embedding

        chunks = Chunk.objects.order_by_similarity(embedding, limit=limit)

        return [
            {
                "source_id": chunk.id,
                "text": chunk.text,
                "context_id": chunk.context_id,
                "score": getattr(chunk, "distance", 0),  # distance, lower is better
            }
            for chunk in chunks
        ]

    def _keyword_search(self, query: str, limit: int) -> list[dict[str, Any]]:
        """Run keyword search using Postgres SearchVector."""
        from django.contrib.postgres.search import SearchRank, SearchVector

        from apps.ai.models.chunk import Chunk

        vector = SearchVector("text")
        chunks = (
            Chunk.objects.annotate(rank=SearchRank(vector, query))
            .filter(rank__gt=0.01)
            .order_by("-rank")[:limit]
        )

        return [
            {
                "source_id": chunk.id,
                "text": chunk.text,
                "context_id": chunk.context_id,
                "score": chunk.rank,
            }
            for chunk in chunks
        ]
