"""Tests for CacheExtension."""

import datetime
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from django.conf import settings
from strawberry.permission import PermissionExtension

from apps.api.internal.extensions.cache import (
    CACHE_MISS,
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
        key1 = generate_key("chapter", {"key": "germany"}, role=None)
        key2 = generate_key("chapter", {"key": "germany"}, role=None)

        assert key1 == key2
        assert key1.startswith("graphql-")
        assert len(key1.split("-")[-1]) == 64  # SHA256 hex digest length

    def test_differs_for_different_field_names(self):
        """Test that different field names produce different keys."""
        key1 = generate_key("chapter", {"key": "germany"}, role=None)
        key2 = generate_key("project", {"key": "germany"}, role=None)

        assert key1 != key2

    def test_differs_for_different_args(self):
        """Test that different arguments produce different keys."""
        key1 = generate_key("chapter", {"key": "germany"}, role=None)
        key2 = generate_key("chapter", {"key": "canada"}, role=None)

        assert key1 != key2

    def test_sorts_args_for_consistency(self):
        """Test that argument order doesn't affect the key."""
        key1 = generate_key("chapter", {"a": "1", "b": "2"}, role=None)
        key2 = generate_key("chapter", {"b": "2", "a": "1"}, role=None)

        assert key1 == key2

    def test_serializes_datetime_and_uuid_args(self):
        """Test that generate_key handles datetime and UUID in args without error."""
        dt = datetime.datetime(2025, 1, 15, 12, 0, 0, tzinfo=datetime.UTC)
        uid = UUID("550e8400-e29b-41d4-a716-446655440000")
        field_args = {"at": dt, "id": uid}

        key1 = generate_key("someField", field_args, role=None)
        key2 = generate_key("someField", field_args, role=None)

        assert key1 == key2
        assert key1.startswith(f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-")

    def test_differs_for_different_roles(self):
        """Test that different roles produce different keys."""
        key1 = generate_key("getProgram", {"programKey": "test"}, role="admin")
        key2 = generate_key("getProgram", {"programKey": "test"}, role="public")

        assert key1 != key2

    def test_same_role_produces_same_key(self):
        """Test that the same role produces the same key."""
        key1 = generate_key("getProgram", {"programKey": "test"}, role="admin")
        key2 = generate_key("getProgram", {"programKey": "test"}, role="admin")

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
        mock_cache.get.return_value = cached_result

        result = extension.resolve(mock_next, None, mock_info, key="germany")

        assert result == cached_result
        mock_cache.get.assert_called_once()
        mock_next.assert_not_called()

    @patch("apps.api.internal.extensions.cache.cache")
    def test_caches_result_on_miss(self, mock_cache, extension, mock_info, mock_next):
        """Test that result is cached on cache miss."""
        mock_cache.get.return_value = CACHE_MISS

        extension.resolve(mock_next, None, mock_info, key="germany")

        mock_next.assert_called_once()
        mock_cache.set.assert_called_once()


class TestInvalidateProgramCache:
    """Test cases for invalidate_program_cache function."""

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_admin_and_public_caches(self, mock_delete):
        """Test that invalidate_program_cache invalidates both admin and public caches."""
        invalidate_program_cache("test-program")
        assert mock_delete.call_count == 4

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_get_program_query(self, mock_delete):
        """Test that invalidate_program_cache invalidates getProgram queries."""
        invalidate_program_cache("test-program")
        calls = mock_delete.call_args_list
        keys = [call[0][0] for call in calls]
        admin_key = generate_key("getProgram", {"programKey": "test-program"}, "admin")
        public_key = generate_key("getProgram", {"programKey": "test-program"}, "public")
        assert admin_key in keys
        assert public_key in keys

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_get_program_modules_query(self, mock_delete):
        """Test that invalidate_program_cache invalidates getProgramModules queries."""
        invalidate_program_cache("test-program")
        calls = mock_delete.call_args_list
        keys = [call[0][0] for call in calls]
        admin_key = generate_key("getProgramModules", {"programKey": "test-program"}, "admin")
        public_key = generate_key("getProgramModules", {"programKey": "test-program"}, "public")
        assert admin_key in keys
        assert public_key in keys


class TestInvalidateModuleCache:
    """Test cases for invalidate_module_cache function."""

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_module_and_program_caches(self, mock_delete):
        """Test that invalidate_module_cache invalidates both module and program caches."""
        invalidate_module_cache("test-module", "test-program")
        assert mock_delete.call_count == 6

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_get_module_query(self, mock_delete):
        """Test that invalidate_module_cache invalidates getModule queries."""
        invalidate_module_cache("test-module", "test-program")

        calls = mock_delete.call_args_list
        keys = [call[0][0] for call in calls]
        admin_key = generate_key(
            "getModule", {"moduleKey": "test-module", "programKey": "test-program"}, "admin"
        )
        public_key = generate_key(
            "getModule", {"moduleKey": "test-module", "programKey": "test-program"}, "public"
        )
        assert admin_key in keys
        assert public_key in keys
