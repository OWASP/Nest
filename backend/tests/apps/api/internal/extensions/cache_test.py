"""Tests for CacheExtension."""

from unittest.mock import MagicMock, patch

import pytest
from strawberry.permission import PermissionExtension

from apps.api.internal.extensions.cache import (
    CacheExtension,
    generate_key,
    get_protected_fields,
    invalidate_module_cache,
    invalidate_program_cache,
)


class TestGenerateKey:
    """Test cases for the generate_key function."""

    def test_creates_deterministic_hash(self):
        """Test that generate_key creates a deterministic hash key."""
        key1 = generate_key("chapter", {"key": "germany"})
        key2 = generate_key("chapter", {"key": "germany"})

        assert key1 == key2
        assert key1.startswith("graphql-")
        assert len(key1.split("-")[-1]) == 64  # SHA256 hex digest length

    def test_differs_for_different_field_names(self):
        """Test that different field names produce different keys."""
        key1 = generate_key("chapter", {"key": "germany"})
        key2 = generate_key("project", {"key": "germany"})

        assert key1 != key2

    def test_differs_for_different_args(self):
        """Test that different arguments produce different keys."""
        key1 = generate_key("chapter", {"key": "germany"})
        key2 = generate_key("chapter", {"key": "canada"})

        assert key1 != key2

    def test_sorts_args_for_consistency(self):
        """Test that argument order doesn't affect the key."""
        key1 = generate_key("chapter", {"a": "1", "b": "2"})
        key2 = generate_key("chapter", {"b": "2", "a": "1"})

        assert key1 == key2


class TestGetProtectedFields:
    """Test cases for the get_protected_fields function."""

    @pytest.fixture
    def mock_schema(self):
        """Return a mock schema with protected and public fields."""
        mock_field_protected = MagicMock()
        mock_field_protected.name = "api_keys"
        mock_field_protected.extensions = [MagicMock(spec=PermissionExtension)]

        mock_field_public = MagicMock()
        mock_field_public.name = "chapters"
        mock_field_public.extensions = []

        mock_query_type = MagicMock()
        mock_query_type.definition.fields = [mock_field_protected, mock_field_public]

        mock_schema = MagicMock()
        mock_schema.schema_converter.type_map.get.return_value = mock_query_type
        return mock_schema

    def test_returns_protected_fields_in_camel_case(self, mock_schema):
        """Test that protected fields are returned in camelCase."""
        get_protected_fields.cache_clear()
        protected = get_protected_fields(mock_schema)

        assert "apiKeys" in protected
        assert "chapters" not in protected

    def test_returns_tuple(self, mock_schema):
        """Test that get_protected_fields returns a tuple."""
        get_protected_fields.cache_clear()
        protected = get_protected_fields(mock_schema)

        assert isinstance(protected, tuple)


class TestResolve:
    """Test cases for the resolve method."""

    @pytest.fixture(autouse=True)
    def mock_protected_fields(self):
        """Patch get_protected_fields for all tests."""
        with patch(
            "apps.api.internal.extensions.cache.get_protected_fields", return_value=("apiKeys",)
        ):
            yield

    @pytest.fixture
    def mock_info(self):
        """Return a mock GraphQL resolve info."""
        mock = MagicMock()
        mock.field_name = "chapter"
        mock.parent_type.name = "Query"
        return mock

    @pytest.fixture
    def mock_next(self):
        """Return a mock next resolver."""
        return MagicMock(return_value={"name": "OWASP"})

    @pytest.fixture
    def extension(self):
        """Return a CacheExtension instance."""
        extension = CacheExtension()
        extension.execution_context = MagicMock()
        return extension

    def test_skips_introspection_queries(self, extension, mock_info, mock_next):
        """Test that introspection queries skip caching."""
        mock_info.field_name = "__schema"

        result = extension.resolve(mock_next, None, mock_info)

        mock_next.assert_called_once()
        assert result == mock_next.return_value

    def test_skips_non_query_fields(self, extension, mock_info, mock_next):
        """Test that non-Query parent types skip caching."""
        mock_info.parent_type.name = "ChapterNode"

        result = extension.resolve(mock_next, None, mock_info)

        mock_next.assert_called_once()
        assert result == mock_next.return_value

    def test_skips_protected_fields(self, extension, mock_info, mock_next):
        """Test that protected fields skip caching."""
        mock_info.field_name = "apiKeys"

        result = extension.resolve(mock_next, None, mock_info)

        mock_next.assert_called_once()
        assert result == mock_next.return_value

    @patch("apps.api.internal.extensions.cache.cache")
    def test_returns_cached_result_on_hit(self, mock_cache, extension, mock_info, mock_next):
        """Test that cached result is returned on cache hit."""
        cached_result = {"name": "Cached OWASP"}
        mock_cache.get_or_set.return_value = cached_result

        result = extension.resolve(mock_next, None, mock_info, key="germany")

        assert result == cached_result
        mock_cache.get_or_set.assert_called_once()
        mock_next.assert_not_called()

    @patch("apps.api.internal.extensions.cache.cache")
    def test_caches_result_on_miss(self, mock_cache, extension, mock_info, mock_next):
        """Test that result is cached on cache miss."""
        mock_cache.get_or_set.side_effect = lambda _key, default, _timeout: default()

        extension.resolve(mock_next, None, mock_info, key="germany")

        mock_next.assert_called_once()
        mock_cache.get_or_set.assert_called_once()


class TestInvalidationHelpers:
    """Test cases for invalidation helper functions."""

    @patch("apps.api.internal.extensions.cache.cache")
    @patch("apps.api.internal.extensions.cache.generate_key")
    def test_invalidate_program_cache_uses_camel_case_keys(self, mock_generate_key, mock_cache):
        """Test that invalidate_program_cache uses correct camelCase keys."""
        mock_generate_key.side_effect = lambda name, _args: f"{name}-hashed"

        invalidate_program_cache("my-program")

        # Verify calls to generate_key use camelCase 'programKey'
        assert mock_generate_key.call_count == 2
        mock_generate_key.assert_any_call("getProgram", {"programKey": "my-program"})
        mock_generate_key.assert_any_call("getProgramModules", {"programKey": "my-program"})

        assert mock_cache.delete.call_count == 2
        mock_cache.delete.assert_any_call("getProgram-hashed")
        mock_cache.delete.assert_any_call("getProgramModules-hashed")

    @patch("apps.api.internal.extensions.cache.cache")
    @patch("apps.api.internal.extensions.cache.generate_key")
    def test_invalidate_module_cache_uses_camel_case_keys(self, mock_generate_key, mock_cache):
        """Test that invalidate_module_cache uses correct camelCase keys."""
        mock_generate_key.side_effect = lambda name, _args: f"{name}-hashed"

        invalidate_module_cache("module-1", "program-1")

        assert mock_generate_key.call_count == 3
        mock_generate_key.assert_any_call(
            "getModule", {"moduleKey": "module-1", "programKey": "program-1"}
        )
        mock_generate_key.assert_any_call("getProgram", {"programKey": "program-1"})
        mock_generate_key.assert_any_call("getProgramModules", {"programKey": "program-1"})

        assert mock_cache.delete.call_count == 3
