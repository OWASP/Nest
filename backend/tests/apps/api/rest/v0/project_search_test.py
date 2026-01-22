"""Tests for structured search utility."""

from unittest.mock import MagicMock

from apps.api.rest.v0.structured_search import apply_structured_search


def test_apply_structured_search_invalid_query():
    """Verify malformed queries fail safely."""
    mock_qs = MagicMock()
    mock_qs.filter.return_value = mock_qs
    schema = {"stars": "number"}

    apply_structured_search(mock_qs, "stars>>>", schema)

    _, kwargs = mock_qs.filter.call_args
    assert kwargs == {}
