from apps.ai.retriever import weighted_reciprocal_rank


def test_weighted_reciprocal_rank():
    """Verify RRF sorting logic."""
    k = 60
    # vectors: A(rank 1), B(rank 2)
    vector_results = [
        {"source_id": "A", "score": 0.9},
        {"source_id": "B", "score": 0.8},
    ]
    # keywords: B(rank 1), C(rank 2)
    bm25_results = [
        {"source_id": "B", "score": 10},
        {"source_id": "C", "score": 5},
    ]

    # Expected scores calculation:
    # A score: 1/(60+1) = 0.01639
    # B score: 1/(60+2) + 1/(60+1) = 0.01612 + 0.01639 = 0.03251
    # C score: 1/(60+2) = 0.01612
    # Order should be B, A, C (B is first)

    results = weighted_reciprocal_rank(vector_results, bm25_results, k=k)

    assert results[0]["source_id"] == "B"
    assert results[0]["rrf_score"] > results[1]["rrf_score"]

    # Verify strict math
    # B score approx 0.0325
    assert 0.032 < results[0]["rrf_score"] < 0.033
