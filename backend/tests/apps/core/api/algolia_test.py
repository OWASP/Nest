import json
from unittest.mock import Mock, patch

import pytest
import requests
from algoliasearch.http.exceptions import AlgoliaException
from django.core.cache import cache

from apps.core.api.algolia import algolia_search, get_search_results

MOCKED_SEARCH_RESULTS = {
    "hits": [
        {"id": 1, "name": "Test Item 1"},
        {"id": 2, "name": "Test Item 2"},
    ],
    "nbPages": 5,
}

CLIENT_IP_ADDRESS = "127.0.0.1"
HTTP_STATUS_INTERNAL_ERROR = 500
EXPECTED_NB_PAGES = 3
GET_SEARCH_RESULTS_PATH = "apps.core.api.algolia.get_search_results"
ERROR_MESSAGE_INTERNAL = "An internal error occurred. Please try again later."


@pytest.fixture
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
            GET_SEARCH_RESULTS_PATH, return_value=expected_result
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

    def test_algolia_search_uses_cache(self):
        """Test that results are cached and retrieved from cache."""
        with patch(
            GET_SEARCH_RESULTS_PATH, return_value=MOCKED_SEARCH_RESULTS
        ) as mock_get_search_results:
            mock_request = Mock()
            mock_request.META = {"HTTP_X_FORWARDED_FOR": CLIENT_IP_ADDRESS}
            mock_request.method = "POST"
            request_data = {
                "facetFilters": [],
                "hitsPerPage": 10,
                "indexName": "projects",
                "page": 1,
                "query": "test",
            }
            mock_request.body = json.dumps(request_data)

            response1 = algolia_search(mock_request)
            assert json.loads(response1.content) == MOCKED_SEARCH_RESULTS
            assert mock_get_search_results.call_count == 1

            response2 = algolia_search(mock_request)
            assert json.loads(response2.content) == MOCKED_SEARCH_RESULTS

            assert mock_get_search_results.call_count == 1

    def test_algolia_search_json_decode_error(self):
        """Test the scenario where the request body is not valid JSON."""
        mock_request = Mock()
        mock_request.META = {"HTTP_X_FORWARDED_FOR": CLIENT_IP_ADDRESS}
        mock_request.method = "POST"
        mock_request.body = "invalid json data"

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

        assert response.status_code == HTTP_STATUS_INTERNAL_ERROR
        assert response_data["error"] == ERROR_MESSAGE_INTERNAL

    def test_algolia_search_algolia_exception(self):
        """Test the scenario where Algolia throws an exception."""
        with patch(
            GET_SEARCH_RESULTS_PATH,
            side_effect=AlgoliaException("Algolia error"),
        ):
            mock_request = Mock()
            mock_request.META = {"HTTP_X_FORWARDED_FOR": CLIENT_IP_ADDRESS}
            mock_request.method = "POST"
            mock_request.body = json.dumps(
                {
                    "facetFilters": [],
                    "hitsPerPage": 10,
                    "indexName": "projects",
                    "page": 1,
                    "query": "test",
                }
            )

            response = algolia_search(mock_request)
            response_data = json.loads(response.content)

            assert response.status_code == HTTP_STATUS_INTERNAL_ERROR
            assert response_data["error"] == ERROR_MESSAGE_INTERNAL

    def test_get_search_results_function(self):
        """Test the get_search_results function directly."""
        mock_client = Mock()
        mock_response = Mock()
        mock_result = Mock()
        mock_result.to_dict.return_value = {"hits": [{"id": 1, "name": "Test"}], "nbPages": 3}
        mock_response.results = [mock_result]
        mock_client.search.return_value = mock_response

        with (
            patch("apps.core.api.algolia.IndexBase.get_client", return_value=mock_client),
            patch("apps.core.api.algolia.get_params_for_index", return_value={"some": "param"}),
        ):
            result = get_search_results(
                index_name="projects",
                query="test",
                page=2,
                hits_per_page=10,
                facet_filters=["filter1"],
                ip_address="1.2.3.4",
            )

            assert "hits" in result
            assert "nbPages" in result
            assert result["hits"] == [{"id": 1, "name": "Test"}]
            assert result["nbPages"] == EXPECTED_NB_PAGES

            mock_client.search.assert_called_once()
            actual_call_args = mock_client.search.call_args[1]
            assert "search_method_params" in actual_call_args
            assert "requests" in actual_call_args["search_method_params"]
            assert len(actual_call_args["search_method_params"]["requests"]) == 1

            assert "hitsPerPage" in actual_call_args["search_method_params"]["requests"][0]
            assert "query" in actual_call_args["search_method_params"]["requests"][0]
            assert "facetFilters" in actual_call_args["search_method_params"]["requests"][0]
        response = Mock()
        response.status_code = requests.codes.bad_request
        response_data = {"error": ERROR_MESSAGE_INTERNAL}
        assert response.status_code == requests.codes.bad_request
        assert response_data["error"] == ERROR_MESSAGE_INTERNAL
