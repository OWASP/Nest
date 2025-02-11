from unittest.mock import patch, Mock

import pytest
import json

from django.core.cache import cache
from apps.owasp.api.search.algolia import algolia_search, get_search_results

MOCKED_SEARCH_RESULTS = {
    "hits": [
        {"id": 1, "name": "Test Item 1"},
        {"id": 2, "name": "Test Item 2"},
    ],
    "nbPages": 5,
}


@pytest.fixture
def clear_cache():
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
def algolia_search(clear_cache, index_name, query, page, hits_per_page, expected_result):
    with patch(
        "apps.owasp.api.search.algolia.get_search_results", return_value=expected_result
    ) as mock_get_search_results:

        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.body = json.dumps({
            "indexName": index_name,
            "query": query,
            "page": page,
            "hitsPerPage": hits_per_page,
        }).encode("utf-8")

        response = algolia_search(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == 200
        assert response_data == expected_result
        mock_get_search_results.assert_called_once_with(index_name, query, page, hits_per_page)


def algolia_search():

    mock_request = Mock()
    mock_request.method = "GET"

    response = algolia_search(mock_request)
    response_data = json.loads(response.content)

    assert response.status_code == 405
    assert response_data["error"] == "Method not allowed"


def algolia_search():

    mock_request = Mock()
    mock_request.method = "POST"
    mock_request.body = b"invalid json"

    response = algolia_search(mock_request)
    response_data = json.loads(response.content)

    assert response.status_code == 500
    assert "error" in response_data


def algolia_search():
    with patch(
        "apps.owasp.api.search.algolia.get_search_results", return_value=None
    ) as mock_get_search_results:

        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.body = json.dumps({
            "indexName": "projects",
            "query": "security",
            "page": 1,
            "hitsPerPage": 10,
        }).encode("utf-8")

        mock_get_search_results.side_effect = Exception("Test error")
        response = algolia_search(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == 500
        assert response_data["error"] == "Test error"
