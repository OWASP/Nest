import pytest

from apps.ai.evaluation.datasets.rag_fixtures import get_rag_fixture


@pytest.mark.parametrize("case_id", ["rag-002", "rag-003"])
@pytest.mark.parametrize("scenario", ["relevant", "irrelevant", "mixed"])
def test_fixture_results_are_independent(case_id, scenario):
    documents = get_rag_fixture(case_id, scenario)
    original_text = documents[0]["text"]
    original_count = len(documents)

    documents[0]["text"] = "Changed by another run"
    documents.append({"text": "Extra", "context": "Extra", "distance": 0.2})

    fresh_documents = get_rag_fixture(case_id, scenario)

    assert len(fresh_documents) == original_count
    assert fresh_documents[0]["text"] == original_text


@pytest.mark.parametrize("case_id", ["rag-002", "rag-003"])
def test_empty_retrieval_returns_no_documents(case_id):
    assert get_rag_fixture(case_id, "empty") == []


@pytest.mark.parametrize("case_id", ["rag-002", "rag-003"])
def test_mixed_fixture_places_unrelated_document_before_support(case_id):
    mixed = get_rag_fixture(case_id, "mixed")

    assert mixed[:1] == get_rag_fixture(case_id, "irrelevant")
    assert mixed[1:] == get_rag_fixture(case_id, "relevant")
