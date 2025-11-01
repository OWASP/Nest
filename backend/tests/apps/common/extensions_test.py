from unittest.mock import MagicMock, patch

import pytest
from strawberry.types.info import Info

from apps.common.extensions import CacheFieldExtension


@pytest.mark.parametrize(
    ("typename", "key", "kwargs", "prefix", "expected_key"),
    [
        ("UserNode", "name", {}, "p1", "p1:UserNode:name:{}"),
        (
            "RepositoryNode",
            "issues",
            {"limit": 10},
            "p2",
            """p2:RepositoryNode:issues:{"limit": 10}""",
        ),
        (
            "RepositoryNode",
            "issues",
            {"limit": 10, "state": "open"},
            "p3",
            """p3:RepositoryNode:issues:{"limit": 10, "state": "open"}""",
        ),
        (
            "RepositoryNode",
            "issues",
            {"state": "open", "limit": 10},
            "p4",
            """p4:RepositoryNode:issues:{"limit": 10, "state": "open"}""",
        ),
    ],
)
def test_generate_key(typename, key, kwargs, prefix, expected_key):
    """Test cases for the generate_key method."""
    mock_info = MagicMock(spec=Info)
    mock_info.path.typename = typename
    mock_info.path.key = key

    extension = CacheFieldExtension(prefix=prefix)
    assert extension.generate_key(mock_info, kwargs) == expected_key


class TestCacheFieldExtensionResolve:
    """Test cases for the resolve method of CacheFieldExtension."""

    @pytest.fixture
    def mock_info(self):
        """Return a mock Strawberry Info object."""
        mock_info = MagicMock(spec=Info)
        mock_info.path.typename = "TestType"
        mock_info.path.key = "testField"
        return mock_info

    @patch("apps.common.extensions.cache")
    def test_resolve_caches_result_on_miss(self, mock_cache, mock_info):
        """Test that the resolver caches the result on a cache miss."""
        mock_cache.get.return_value = None
        resolver_result = "some data"
        next_ = MagicMock(return_value=resolver_result)
        extension = CacheFieldExtension(cache_timeout=60)

        result = extension.resolve(next_, source=None, info=mock_info)

        assert result == resolver_result
        mock_cache.get.assert_called_once()
        next_.assert_called_once()
        mock_cache.set.assert_called_once()
        mock_cache.set.assert_called_with(mock_cache.get.call_args[0][0], resolver_result, 60)

    @patch("apps.common.extensions.cache")
    def test_resolve_returns_cached_result_on_hit(self, mock_cache, mock_info):
        """Test that the resolver returns the cached result on a cache hit."""
        cached_result = "cached data"
        mock_cache.get.return_value = cached_result
        next_ = MagicMock()
        extension = CacheFieldExtension()

        result = extension.resolve(next_, source=None, info=mock_info)

        assert result == cached_result
        mock_cache.get.assert_called_once()
        next_.assert_not_called()
        mock_cache.set.assert_not_called()

    @pytest.mark.parametrize("falsy_result", [None, [], {}, 0, False])
    @patch("apps.common.extensions.cache")
    def test_resolve_does_not_cache_falsy_result(self, mock_cache, falsy_result, mock_info):
        """Test that the resolver does not cache None or other falsy results."""
        mock_cache.get.return_value = None
        next_ = MagicMock(return_value=falsy_result)
        extension = CacheFieldExtension()

        result = extension.resolve(next_, source=None, info=mock_info)

        assert result == falsy_result
        mock_cache.get.assert_called_once()
        next_.assert_called_once()
        mock_cache.set.assert_not_called()
