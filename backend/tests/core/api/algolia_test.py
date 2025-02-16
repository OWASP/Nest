import json
from unittest.mock import Mock, patch

import pytest
import requests
from django.core.cache import cache

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


@pytest.mark.usefixtures("_clear_cache")
class TestAlgoliaSearch:
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
    def test_algolia_search_valid_request(
        self, index_name, query, page, hits_per_page, expected_result
    ):
        """Test valid requests for the algolia_search."""
        with patch(
            "apps.core.api.algolia.get_search_results", return_value=expected_result
        ) as mock_get_search_results:
            mock_request = Mock()
            mock_request.method = "POST"
            mock_request.body = json.dumps(
                {
                    "indexName": index_name,
                    "query": query,
                    "page": page,
                    "hitsPerPage": hits_per_page,
                }
            )

            response = algolia_search(mock_request)
            response_data = json.loads(response.content)

            assert response.status_code == requests.codes.ok
            assert response_data == expected_result
            mock_get_search_results.assert_called_once_with(index_name, query, page, hits_per_page)

    def test_algolia_search_invalid_method(self):
        """Test the scenario where the HTTP method is not POST."""
        mock_request = Mock()
        mock_request.method = "GET"

        response = algolia_search(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == requests.codes.method_not_allowed
        assert response_data["error"] == "Method not allowed"
