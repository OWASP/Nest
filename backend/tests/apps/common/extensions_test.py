from unittest.mock import MagicMock, patch

import pytest
from strawberry.types.info import Info

from apps.common.extensions import CacheFieldExtension


class MockPath:
    def __init__(self, key, typename, prev=None):
        self.key = key
        self.prev = prev
        self.typename = typename


class MockSource:
    def __init__(self, id=None):  # noqa: A002
        self.id = id


@pytest.mark.parametrize(
    ("source", "path", "kwargs", "prefix", "expected_key"),
    [
        (
            None,
            MockPath(key="repository", typename="Query"),
            {"organization_key": "OWASP", "repository_key": "nest"},
            "p1",
            'p1:repository:{"organization_key": "OWASP", "repository_key": "nest"}',
        ),
        (
            MockSource(id=123),
            MockPath(
                key="organization",
                typename="RepositoryNode",
                prev=MockPath(key="repository", typename="Query"),
            ),
            {},
            "p2",
            'p2:repository.organization:{"__source_id__": "123"}',
        ),
        (
            MockSource(id=0),
            MockPath(
                key="organization",
                typename="RepositoryNode",
                prev=MockPath(key="repository", typename="Query"),
            ),
            {},
            "p3",
            'p3:repository.organization:{"__source_id__": "0"}',
        ),
        (
            MockSource(),
            MockPath(
                key="organization",
                typename="RepositoryNode",
                prev=MockPath(key="repository", typename="Query"),
            ),
            {},
            "p4",
            "p4:repository.organization:{}",
        ),
        (
            None,
            MockPath(
                key="badgeCount",
                typename="UserNode",
                prev=MockPath(
                    key="author",
                    typename="IssueNode",
                    prev=MockPath(
                        key=0,
                        typename=None,
                        prev=MockPath(
                            key="issues",
                            typename="RepositoryNode",
                            prev=MockPath(key="repository", typename="Query"),
                        ),
                    ),
                ),
            ),
            {},
            "graphql-resolver",
            "graphql-resolver:repository.issues.0.author.badgeCount:{}",
        ),
    ],
)
def test_generate_key(source, path, kwargs, prefix, expected_key):
    """Test cases for the generate_key method."""
    mock_info = MagicMock(spec=Info)
    mock_info.path = path

    extension = CacheFieldExtension(prefix=prefix)
    assert extension.generate_key(source, mock_info, kwargs) == expected_key


class TestCacheFieldExtensionResolve:
    """Test cases for the resolve method of CacheFieldExtension."""

    @pytest.fixture
    def mock_info(self):
        """Return a mock Strawberry Info object."""
        mock_info = MagicMock(spec=Info)
        mock_info.path = MockPath(key="testField", typename="TestType", prev=None)
        return mock_info

    @patch("apps.common.extensions.cache")
    def test_resolve_caches_result_on_miss(self, mock_cache, mock_info):
        """Test that get_or_set calls the resolver on a cache miss."""
        resolver_result = "some data"
        next_ = MagicMock(return_value=resolver_result)
        extension = CacheFieldExtension(cache_timeout=60)

        def cache_miss_side_effect(key, default_callable, timeout=None):  # noqa: ARG001
            return default_callable()

        mock_cache.get_or_set.side_effect = cache_miss_side_effect

        result = extension.resolve(next_, source=None, info=mock_info)

        assert result == resolver_result
        mock_cache.get_or_set.assert_called_once()
        next_.assert_called_once()

    @patch("apps.common.extensions.cache")
    def test_resolve_returns_cached_result_on_hit(self, mock_cache, mock_info):
        """Test that the resolver returns the cached result on a cache hit."""
        cached_result = "cached data"
        mock_cache.get_or_set.return_value = cached_result
        next_ = MagicMock()
        extension = CacheFieldExtension()

        result = extension.resolve(next_, source=None, info=mock_info)

        assert result == cached_result
        mock_cache.get_or_set.assert_called_once()
        next_.assert_not_called()

    @pytest.mark.parametrize("falsy_result", [None, [], {}, 0, False])
    @patch("apps.common.extensions.cache")
    def test_resolve_caches_falsy_result(self, mock_cache, falsy_result, mock_info):
        """Test that the resolver caches None and other falsy results."""
        next_ = MagicMock(return_value=falsy_result)
        extension = CacheFieldExtension()

        def cache_miss_side_effect(key, default_callable, timeout=None):  # noqa: ARG001
            return default_callable()

        mock_cache.get_or_set.side_effect = cache_miss_side_effect
        result = extension.resolve(next_, source=None, info=mock_info)

        assert result == falsy_result
        mock_cache.get_or_set.assert_called_once()
        next_.assert_called_once()
