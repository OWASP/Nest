import pytest

from apps.ai.evaluation.datasets.rag_fixtures import get_rag_fixture


@pytest.mark.parametrize("scenario", ["relevant", "irrelevant"])
def test_fixture_results_are_independent(scenario):
    documents = get_rag_fixture("rag-002", scenario)
    original_text = documents[0]["text"]
    original_count = len(documents)

    documents[0]["text"] = "Changed by another run"
    documents.append({"text": "Extra", "context": "Extra", "distance": 0.2})

    fresh_documents = get_rag_fixture("rag-002", scenario)

    assert len(fresh_documents) == original_count
    assert fresh_documents[0]["text"] == original_text


def test_empty_retrieval_returns_no_documents():
    assert get_rag_fixture("rag-002", "empty") == []


@pytest.mark.parametrize(
    ("case_id", "scenario"),
    [
        ("unknown-case", "relevant"),
        ("rag-002", "unknown-scenario"),
    ],
)
def test_unknown_fixture_is_rejected(case_id, scenario):
    with pytest.raises(KeyError):
        get_rag_fixture(case_id, scenario)