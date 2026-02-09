import json
from http import HTTPStatus
from unittest.mock import Mock, patch

import pytest

from apps.core.api.internal.algolia import CACHE_TTL_IN_SECONDS, algolia_search
from apps.core.constants import CACHE_PREFIX

MOCKED_SEARCH_RESULTS = {
    "hits": [
        {"id": 1, "name": "Test Item 1"},
        {"id": 2, "name": "Test Item 2"},
    ],
    "nbPages": 5,
}

CLIENT_IP_ADDRESS = "127.0.0.1"


@pytest.fixture(autouse=True)
def mock_redis_cache():
    """Mock Redis cache used in algolia.py."""
    with patch("apps.core.api.internal.algolia.cache") as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        yield mock_cache


class TestAlgoliaSearch:
    def _build_request(self, *, facet_filters, hits_per_page, index_name, page, query):
        """Build mock requests with consistent structure."""
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
        return mock_request

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
            "apps.core.api.internal.algolia.get_search_results", return_value=expected_result
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

            assert response.status_code == HTTPStatus.OK
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

        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        assert response_data["error"] == "Method GET is not allowed"

    @pytest.mark.parametrize(
        ("index_name", "query", "page", "hits_per_page", "facet_filters", "error_message"),
        [
            (
                5,
                "owasp",
                2,
                20,
                ["idx_is_active:true"],
                "indexName is required and must be a string.",
            ),
            (
                "chapters",
                5,
                2,
                20,
                ["idx_is_active:true"],
                "query must be a string.",
            ),
            (
                "committees",
                "review",
                "0",
                5,
                [],
                "page value must be an integer.",
            ),
            (
                "committees",
                "review",
                1,
                "1001",
                [],
                "hitsPerPage must be an integer.",
            ),
            (
                "issues",
                "bug",
                1,
                10,
                "idx_is_active:true",
                "facetFilters must be a list.",
            ),
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

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response_data["error"] == error_message

    def test_algolia_search_different_facet_filters_return_different_results(self):
        """Test that same query with different facet filters returns different results."""
        result_active = {
            "hits": [{"id": 1, "name": "Active Item"}],
            "nbPages": 1,
        }
        result_inactive = {
            "hits": [{"id": 2, "name": "Inactive Item"}],
            "nbPages": 1,
        }
        base_params = {
            "index_name": "projects",
            "query": "security",
            "page": 1,
            "hits_per_page": 10,
        }

        with patch(
            "apps.core.api.internal.algolia.get_search_results",
            side_effect=[result_active, result_inactive],
        ):
            mock_request_1 = self._build_request(
                facet_filters=["idx_is_active:true"],
                **base_params,
            )
            mock_request_2 = self._build_request(
                facet_filters=["idx_is_active:false"],
                **base_params,
            )

            response_1 = algolia_search(mock_request_1)
            response_2 = algolia_search(mock_request_2)

            response_data_1 = json.loads(response_1.content)
            response_data_2 = json.loads(response_2.content)

            assert response_1.status_code == HTTPStatus.OK
            assert response_2.status_code == HTTPStatus.OK
            assert response_data_1 == result_active
            assert response_data_2 == result_inactive
            assert response_data_1 != response_data_2

    def test_algolia_search_same_query_same_keys_return_same_results(self, mock_redis_cache):
        """Test that cache hit returns same results without re-querying backend."""
        expected_result = MOCKED_SEARCH_RESULTS
        facet_filters = ["idx_is_active:true"]
        base_params = {
            "facet_filters": facet_filters,
            "index_name": "projects",
            "query": "security",
            "page": 1,
            "hits_per_page": 10,
        }

        mock_redis_cache.get.side_effect = [None, expected_result]

        with patch(
            "apps.core.api.internal.algolia.get_search_results", return_value=expected_result
        ) as mock_get_search_results:
            mock_request = self._build_request(**base_params)

            response_1 = algolia_search(mock_request)
            response_2 = algolia_search(mock_request)

            response_data_1 = json.loads(response_1.content)
            response_data_2 = json.loads(response_2.content)

            assert response_1.status_code == HTTPStatus.OK
            assert response_2.status_code == HTTPStatus.OK
            assert response_data_1 == expected_result
            assert response_data_2 == expected_result
            #backend only called once = caching worked
            mock_get_search_results.assert_called_once()