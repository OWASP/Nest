"""Tests for GitHub user search API."""

from unittest.mock import patch

from apps.github.api.search.user import User, get_users, raw_search

DEFAULT_HITS_PER_PAGE = 25
DEFAULT_MIN_PROXIMITY = 4
test_query = "test query"


class TestUserSearch:
    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_with_default_params(self, mock_raw_search):
        """Test get_users with default parameters."""
        query = test_query
        mock_raw_search.return_value = {"hits": [{"idx_login": "testuser"}]}

        result = get_users(query)

        mock_raw_search.assert_called_once()

        args, _ = mock_raw_search.call_args

        assert args[0] == User
        assert args[1] == query
        params = args[2]

        assert params["hitsPerPage"] == DEFAULT_HITS_PER_PAGE
        assert params["page"] == 0
        assert params["minProximity"] == DEFAULT_MIN_PROXIMITY
        assert params["typoTolerance"] == "min"
        assert "attributesToRetrieve" in params

        assert result == {"hits": [{"idx_login": "testuser"}]}

    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_with_none_query(self, mock_raw_search):
        """Test get_users with None as query parameter."""
        mock_raw_search.return_value = {"hits": [{"idx_login": "testuser"}]}
        result = get_users(query=None)
        mock_raw_search.assert_called_once()
        args, _ = mock_raw_search.call_args

        assert args[1] == ""

        assert result == {"hits": [{"idx_login": "testuser"}]}

    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_with_custom_attributes(self, mock_raw_search):
        """Test get_users with custom attributes."""
        query = test_query
        custom_attributes = ["idx_login", "idx_email"]
        mock_raw_search.return_value = {"hits": [{"idx_login": "testuser"}]}

        result = get_users(query, attributes=custom_attributes)

        mock_raw_search.assert_called_once()
        args, _ = mock_raw_search.call_args
        params = args[2]
        assert params["attributesToRetrieve"] == custom_attributes
        assert result == {"hits": [{"idx_login": "testuser"}]}

    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_with_custom_limit_and_page(self, mock_raw_search):
        """Test get_users with custom limit and page."""
        query = test_query
        custom_limit = 50
        custom_page = 3
        mock_raw_search.return_value = {"hits": [{"idx_login": "testuser"}]}

        result = get_users(query, limit=custom_limit, page=custom_page)

        mock_raw_search.assert_called_once()

        args, _ = mock_raw_search.call_args
        params = args[2]
        assert params["hitsPerPage"] == custom_limit
        assert params["page"] == custom_page - 1
        assert result == {"hits": [{"idx_login": "testuser"}]}

    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_with_searchable_attributes(self, mock_raw_search):
        """Test get_users with searchable attributes."""
        query = test_query
        searchable_attributes = ["idx_login", "idx_name"]
        mock_raw_search.return_value = {"hits": [{"idx_login": "testuser"}]}

        result = get_users(query, searchable_attributes=searchable_attributes)

        mock_raw_search.assert_called_once()

        args, _ = mock_raw_search.call_args
        params = args[2]
        assert params["restrictSearchableAttributes"] == searchable_attributes
        assert result == {"hits": [{"idx_login": "testuser"}]}

    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_with_all_custom_parameters(self, mock_raw_search):
        """Test get_users with all custom parameters."""
        query = test_query
        custom_attributes = ["idx_login", "idx_email"]
        custom_limit = 10
        custom_page = 5
        searchable_attributes = ["idx_login"]
        mock_raw_search.return_value = {"hits": [{"idx_login": "testuser"}]}

        result = get_users(
            query,
            attributes=custom_attributes,
            limit=custom_limit,
            page=custom_page,
            searchable_attributes=searchable_attributes,
        )

        mock_raw_search.assert_called_once()

        args, _ = mock_raw_search.call_args
        params = args[2]
        assert params["attributesToRetrieve"] == custom_attributes
        assert params["hitsPerPage"] == custom_limit
        assert params["page"] == custom_page - 1
        assert params["restrictSearchableAttributes"] == searchable_attributes
        assert result == {"hits": [{"idx_login": "testuser"}]}

    def test_raw_search_direct_call(self):
        """Test direct call to raw_search function."""
        with patch("apps.github.api.search.user.algolia_raw_search") as mock_algolia_raw_search:
            mock_algolia_raw_search.return_value = {"hits": [{"idx_login": "testuser"}]}
            model_class = User
            query = "test"
            params = {"param1": "value1"}

            result = raw_search(model_class, query, params)

            mock_algolia_raw_search.assert_called_once_with(model_class, query, params)
            assert result == {"hits": [{"idx_login": "testuser"}]}
