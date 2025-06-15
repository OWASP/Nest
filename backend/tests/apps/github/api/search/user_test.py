"""Test cases for the get_users function in the GitHub user search API module."""

from unittest.mock import patch

from apps.github.api.search.user import get_users


class TestGetUsers:
    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_default_params(self, mock_raw_search):
        mock_raw_search.return_value = {
            "hits": [],
            "nbHits": 0,
        }
        result = get_users("test-query")

        assert result == {
            "hits": [],
            "nbHits": 0,
        }

        called_args = mock_raw_search.call_args[0]

        assert called_args[0].__name__ == "User"
        assert called_args[1] == "test-query"

        params = called_args[2]

        assert params["hitsPerPage"] == 25
        assert params["page"] == 0
        assert params["minProximity"] == 4
        assert params["typoTolerance"] == "min"
        assert "attributesToRetrieve" in params
        assert isinstance(params["attributesToRetrieve"], list)
        assert params["attributesToHighlight"] == []
        assert "restrictSearchableAttributes" not in params

    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_with_custom_params(self, mock_raw_search):
        mock_raw_search.return_value = {
            "hits": [1, 2],
            "nbHits": 2,
        }
        attrs = ["idx_name", "idx_email"]
        result = get_users(
            query="foo",
            attributes=attrs,
            limit=10,
            page=3,
            searchable_attributes=["idx_name"],
        )

        assert result == {
            "hits": [1, 2],
            "nbHits": 2,
        }

        called_args = mock_raw_search.call_args[0]
        params = called_args[2]

        assert params["attributesToRetrieve"] == attrs
        assert params["hitsPerPage"] == 10
        assert params["page"] == 2
        assert params["restrictSearchableAttributes"] == ["idx_name"]

    @patch("apps.github.api.search.user.raw_search")
    def test_get_users_without_searchable_attributes(self, mock_raw_search):
        mock_raw_search.return_value = {
            "hits": ["a"],
            "nbHits": 1,
        }
        result = get_users(
            query="bar",
            attributes=["idx_name"],
            limit=5,
            page=2,
        )

        assert result == {
            "hits": ["a"],
            "nbHits": 1,
        }

        called_args = mock_raw_search.call_args[0]
        params = called_args[2]

        assert "restrictSearchableAttributes" not in params
