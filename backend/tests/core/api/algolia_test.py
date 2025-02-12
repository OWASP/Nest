import json
from unittest.mock import Mock, patch
import pytest
from django.core.cache import cache
import requests

from apps.core.api.algolia import algolia_search

MOCKED_SEARCH_RESULTS = {
    "hits": [
        {"id": 1, "name": "Test Item 1"},
        {"id": 2, "name": "Test Item 2"},
    ],
    "nbPages": 5,
}


@pytest.fixture()
def _clear_cache():
    """Clear the cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.parametrize(
    ("index_name", "query", "page", "hits_per_page", "expected_result"),
    [
        ("projects", "security", 1, 10, MOCKED_SEARCH_RESULTS),
        ("chapters", "owasp", 2, 20, MOCKED_SEARCH_RESULTS),
        ("users", "john", 1, 10, MOCKED_SEARCH_RESULTS),
        ("committees", "review", 1, 10, MOCKED_SEARCH_RESULTS),
        ("issues", "bug", 1, 10, MOCKED_SEARCH_RESULTS),
    ],
)

@pytest.mark.usefixtures("_clear_cache")
def test_algolia_search_valid_request(index_name, query, page, hits_per_page, expected_result):
    """Test valid requests for the algolia_search."""
    with patch(
        "apps.core.api.algolia.get_search_results", return_value=expected_result
    ) as mock_get_search_results:
        mock_request = Mock()
        mock_request.method = "GET"

        mock_request.GET = {
            "indexName": index_name,
            "query": query,
            "page": str(page),
            "hitsPerPage": str(hits_per_page),
        }

        response = algolia_search(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == requests.codes.ok
        assert response_data == expected_result
        mock_get_search_results.assert_called_once_with(index_name, query, page, hits_per_page)


def test_algolia_search_invalid_method():
    """Test the scenario where the HTTP method is not GET."""
    mock_request = Mock()
    mock_request.method = "POST"

    response = algolia_search(mock_request)
    response_data = json.loads(response.content)

    assert response.status_code == requests.codes.method_not_allowed
    assert response_data["error"] == "Method not allowed"
