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

CLIENT_IP_ADDRESS = "127.0.0.1"


@pytest.fixture()
def _clear_cache():
    """Clear the cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.usefixtures("_clear_cache")
class TestAlgoliaSearch:
    @pytest.mark.parametrize(
        ("index_name", "query", "page", "hits_per_page", "facet_filters", "expected_result"),
        [
            ("projects", "security", 1, 10, ["idx_is_active:true"], MOCKED_SEARCH_RESULTS),
            ("chapters", "owasp", 2, 20, ["idx_is_active:true"], MOCKED_SEARCH_RESULTS),
            ("users", "john", 1, 10, [], MOCKED_SEARCH_RESULTS),
            ("committees", "review", 1, 10, [], MOCKED_SEARCH_RESULTS),
            ("issues", "bug", 1, 10, [], MOCKED_SEARCH_RESULTS),
        ],
    )
    def test_algolia_search_valid_request(
        self,
        index_name,
        query,
        page,
        hits_per_page,
        facet_filters,
        expected_result,
    ):
        """Test valid requests for the algolia_search."""
        with patch(
            "apps.core.api.algolia.get_search_results", return_value=expected_result
        ) as mock_get_search_results:
            mock_request = Mock()
            mock_request.META = {"HTTP_X_FORWARDED_FOR": CLIENT_IP_ADDRESS}
            mock_request.method = "POST"
            mock_request.body = json.dumps(
                {
                    "facetFilters": facet_filters,
                    "hitsPerPage": hits_per_page,
                    "indexName": index_name,
                    "page": page,
                    "query": query,
                }
            )

            response = algolia_search(mock_request)
            response_data = json.loads(response.content)

            assert response.status_code == requests.codes.ok
            assert response_data == expected_result
            mock_get_search_results.assert_called_once_with(
                index_name,
                query,
                page,
                hits_per_page,
                facet_filters,
                ip_address=CLIENT_IP_ADDRESS,
            )

    def test_algolia_search_invalid_method(self):
        """Test the scenario where the HTTP method is not POST."""
        mock_request = Mock()
        mock_request.method = "GET"

        response = algolia_search(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == requests.codes.method_not_allowed
        assert response_data["error"] == "Method GET is not allowed"

    @pytest.mark.parametrize(
        ("index_name", "query", "page", "hits_per_page", "facet_filters", "error_message"),
        [
            # Index name tests
            (
                5,
                "owasp",
                2,
                20,
                ["idx_is_active:true"],
                "indexName is required and must be a string.",
            ),
            # Query tests
            ("chapters", 5, 2, 20, ["idx_is_active:true"], "query must be a string."),
            # Page tests
            ("committees", "review", "0", 5, [], "page value must be an integer."),
            # hitsPerPage tests
            ("committees", "review", 1, "1001", [], "hitsPerPage must be an integer."),
            # Facet filters tests
            ("issues", "bug", 1, 10, "idx_is_active:true", "facetFilters must be a list."),
        ],
    )
    def test_algolia_search_invalid_request(
        self,
        index_name,
        query,
        page,
        hits_per_page,
        facet_filters,
        error_message,
    ):
        """Test invalid requests for the algolia_search."""
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.body = json.dumps(
            {
                "facetFilters": facet_filters,
                "hitsPerPage": hits_per_page,
                "indexName": index_name,
                "page": page,
                "query": query,
            }
        )

        response = algolia_search(mock_request)
        response_data = json.loads(response.content)

        assert response.status_code == requests.codes.bad_request
        assert response_data["error"] == error_message
