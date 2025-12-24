"""Hybrid retrieval utilities for combining search results.

Implements Reciprocal Rank Fusion (RRF) to merge vector and keyword
search results into a single ranked list.
"""

from __future__ import annotations

from typing import Any

# Fixed constants per project requirements
RRF_K = 60  # Smoothing constant for RRF formula
HNSW_M = 16  # HNSW index parameter (for reference)


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

    """
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
