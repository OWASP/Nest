"""Tests for CacheExtension."""

from unittest.mock import MagicMock, patch

import pytest
from graphql import OperationType
from strawberry.types import ExecutionContext

from apps.common.extensions import CacheExtension


class TestCacheExtension:
    """Test cases for the CacheExtension class."""

    @pytest.fixture
    def mock_request(self):
        """Return a mock request with unauthenticated user."""
        mock = MagicMock()
        mock.user.is_authenticated = False
        return mock

    @pytest.fixture
    def mock_execution_context(self, mock_request):
        """Return a mock execution context."""
        mock = MagicMock(spec=ExecutionContext)
        mock.query = 'query { repository(key: "test") { name } }'
        mock.variables = {"organization_key": "OWASP", "repository_key": "nest"}
        mock.operation_type = OperationType.QUERY
        mock.context.request = mock_request
        return mock

    @pytest.fixture
    def extension(self, mock_execution_context):
        """Return a CacheExtension instance with a mocked execution context."""
        extension = CacheExtension()
        extension.execution_context = mock_execution_context
        return extension

    def test_generate_key_creates_hash(self, extension, mock_execution_context):
        """Test that generate_key creates a deterministic hash key."""
        key1 = extension.generate_key(mock_execution_context)
        key2 = extension.generate_key(mock_execution_context)

        assert key1 == key2
        assert key1.startswith("graphql-")
        assert len(key1.split("-")[-1]) == 64  # SHA256 hex digest length

    def test_generate_key_differs_for_different_queries(self, extension):
        """Test that different queries produce different keys."""
        context1 = MagicMock(spec=ExecutionContext)
        context1.query = "query { repository { name } }"
        context1.variables = {}

        context2 = MagicMock(spec=ExecutionContext)
        context2.query = "query { project { name } }"
        context2.variables = {}

        key1 = extension.generate_key(context1)
        key2 = extension.generate_key(context2)

        assert key1 != key2

    def test_generate_key_differs_for_different_variables(self, extension):
        """Test that different variables produce different keys."""
        context1 = MagicMock(spec=ExecutionContext)
        context1.query = "query { repository { name } }"
        context1.variables = {"key": "nest"}

        context2 = MagicMock(spec=ExecutionContext)
        context2.query = "query { repository { name } }"
        context2.variables = {"key": "owasp-web"}

        key1 = extension.generate_key(context1)
        key2 = extension.generate_key(context2)

        assert key1 != key2


class TestShouldSkipCache:
    """Test cases for the should_skip_cache method."""

    @pytest.fixture
    def extension(self):
        """Return a CacheExtension instance."""
        return CacheExtension()

    def test_skips_cache_for_mutations(self, extension):
        """Test that mutations are not cached."""
        context = MagicMock(spec=ExecutionContext)
        context.operation_type = OperationType.MUTATION

        assert extension.should_skip_cache(context) is True

    def test_skips_cache_for_subscriptions(self, extension):
        """Test that subscriptions are not cached."""
        context = MagicMock(spec=ExecutionContext)
        context.operation_type = OperationType.SUBSCRIPTION

        assert extension.should_skip_cache(context) is True

    def test_skips_cache_for_authenticated_queries(self, extension):
        """Test that authenticated queries are not cached."""
        context = MagicMock(spec=ExecutionContext)
        context.operation_type = OperationType.QUERY
        context.context.request.user.is_authenticated = True

        assert extension.should_skip_cache(context) is True

    def test_caches_unauthenticated_queries(self, extension):
        """Test that unauthenticated queries are cached."""
        context = MagicMock(spec=ExecutionContext)
        context.operation_type = OperationType.QUERY
        context.context.request.user.is_authenticated = False

        assert extension.should_skip_cache(context) is False


class TestOnExecute:
    """Test cases for the on_execute method."""

    @pytest.fixture
    def mock_request(self):
        """Return a mock request with unauthenticated user."""
        mock = MagicMock()
        mock.user.is_authenticated = False
        return mock

    @pytest.fixture
    def mock_execution_context(self, mock_request):
        """Return a mock execution context for a query."""
        mock = MagicMock(spec=ExecutionContext)
        mock.query = "query { repository { name } }"
        mock.variables = {}
        mock.operation_type = OperationType.QUERY
        mock.context.request = mock_request
        return mock

    @pytest.fixture
    def extension(self, mock_execution_context):
        """Return a CacheExtension instance."""
        extension = CacheExtension()
        extension.execution_context = mock_execution_context
        return extension

    @patch("apps.common.extensions.cache")
    def test_skips_cache_for_mutations(self, mock_cache, extension, mock_execution_context):
        """Test that mutations skip caching entirely."""
        mock_execution_context.operation_type = OperationType.MUTATION

        generator = extension.on_execute()
        next(generator)  # Yields once to let execution continue

        with pytest.raises(StopIteration):
            next(generator)  # Then stops

        mock_cache.get.assert_not_called()
        mock_cache.set.assert_not_called()

    @patch("apps.common.extensions.cache")
    def test_skips_cache_for_authenticated_queries(
        self, mock_cache, extension, mock_execution_context
    ):
        """Test that authenticated queries skip caching."""
        mock_execution_context.context.request.user.is_authenticated = True

        generator = extension.on_execute()
        next(generator)  # Yields once to let execution continue

        with pytest.raises(StopIteration):
            next(generator)  # Then stops

        mock_cache.get.assert_not_called()
        mock_cache.set.assert_not_called()

    @patch("apps.common.extensions.cache")
    def test_returns_cached_result_on_hit(self, mock_cache, extension, mock_execution_context):
        """Test that cached result is returned on cache hit."""
        cached_result = {"data": {"repository": {"name": "Nest"}}}
        mock_cache.get.return_value = cached_result

        generator = extension.on_execute()
        next(generator)

        assert mock_execution_context.result == cached_result
        mock_cache.get.assert_called_once()
        mock_cache.set.assert_not_called()

    @patch("apps.common.extensions.cache")
    def test_caches_result_on_miss(self, mock_cache, extension, mock_execution_context):
        """Test that result is cached on cache miss."""
        mock_cache.get.return_value = None
        resolver_result = {"data": {"repository": {"name": "Nest"}}}
        mock_execution_context.result = resolver_result

        generator = extension.on_execute()
        next(generator)  # First yield (cache miss path)

        with pytest.raises(StopIteration):
            next(generator)  # Second yield + cache.set

        mock_cache.get.assert_called_once()
        mock_cache.set.assert_called_once()

    @pytest.mark.parametrize("falsy_result", [None, [], {}, 0, False])
    @patch("apps.common.extensions.cache")
    def test_caches_falsy_results(
        self, mock_cache, falsy_result, extension, mock_execution_context
    ):
        """Test that falsy results are cached properly."""
        mock_cache.get.return_value = None
        mock_execution_context.result = falsy_result

        generator = extension.on_execute()
        next(generator)

        with pytest.raises(StopIteration):
            next(generator)

        mock_cache.set.assert_called_once()
