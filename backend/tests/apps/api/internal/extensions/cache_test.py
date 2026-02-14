"""Tests for CacheExtension."""

import asyncio
import datetime
from unittest.mock import MagicMock, Mock, patch
from uuid import UUID

import pytest
from django.conf import settings
from django.db.models import QuerySet
from strawberry.permission import PermissionExtension

from apps.api.internal.extensions.cache import (
    CACHE_MISS,
    CacheExtension,
    _get_user_role,
    generate_key,
    get_protected_fields,
    invalidate_cache,
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
        assert key1.startswith(f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-")
        assert len(key1.split("-")[-1]) == 64

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

    @patch("apps.api.internal.extensions.cache.Module")
    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_admin_and_public_caches(self, mock_delete, mock_module_class):
        """Test that invalidate_program_cache invalidates both admin and public caches."""
        mock_module_class.objects.filter.return_value = []
        invalidate_program_cache("test-program")
        assert mock_delete.call_count == 4

    @patch("apps.api.internal.extensions.cache.Module")
    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_get_program_query(self, mock_delete, mock_module_class):
        """Test that invalidate_program_cache invalidates getProgram queries."""
        mock_module_class.objects.filter.return_value = []
        invalidate_program_cache("test-program")
        calls = mock_delete.call_args_list
        keys = [call[0][0] for call in calls]
        admin_key = generate_key("getProgram", {"programKey": "test-program"}, "admin")
        public_key = generate_key("getProgram", {"programKey": "test-program"}, "public")
        assert admin_key in keys
        assert public_key in keys

    @patch("apps.api.internal.extensions.cache.Module")
    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_get_program_modules_query(self, mock_delete, mock_module_class):
        """Test that invalidate_program_cache invalidates getProgramModules queries."""
        mock_module_class.objects.filter.return_value = []
        invalidate_program_cache("test-program")
        calls = mock_delete.call_args_list
        keys = [call[0][0] for call in calls]
        admin_key = generate_key("getProgramModules", {"programKey": "test-program"}, "admin")
        public_key = generate_key("getProgramModules", {"programKey": "test-program"}, "public")
        assert admin_key in keys
        assert public_key in keys

    @patch("apps.api.internal.extensions.cache.Module")
    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_all_module_caches(self, mock_delete, mock_module_class):
        """Test that invalidate_program_cache invalidates all module caches for the program."""
        mock_module1 = Mock(key="module-1")
        mock_module2 = Mock(key="module-2")
        mock_module_class.objects.filter.return_value = [mock_module1, mock_module2]

        invalidate_program_cache("test-program")

        assert mock_delete.call_count == 8

        calls = mock_delete.call_args_list
        keys = [call[0][0] for call in calls]

        module1_admin_key = generate_key(
            "getModule", {"moduleKey": "module-1", "programKey": "test-program"}, "admin"
        )
        module1_public_key = generate_key(
            "getModule", {"moduleKey": "module-1", "programKey": "test-program"}, "public"
        )
        module2_admin_key = generate_key(
            "getModule", {"moduleKey": "module-2", "programKey": "test-program"}, "admin"
        )
        module2_public_key = generate_key(
            "getModule", {"moduleKey": "module-2", "programKey": "test-program"}, "public"
        )

        assert module1_admin_key in keys
        assert module1_public_key in keys
        assert module2_admin_key in keys
        assert module2_public_key in keys


class TestInvalidateModuleCache:
    """Test cases for invalidate_module_cache function."""

    @patch("apps.api.internal.extensions.cache.Module")
    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_module_and_program_caches(self, mock_delete, mock_module_class):
        """Test that invalidate_module_cache invalidates both module and program caches."""
        mock_module_class.objects.filter.return_value = []
        invalidate_module_cache("test-module", "test-program")
        assert mock_delete.call_count == 6

    @patch("apps.api.internal.extensions.cache.Module")
    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_invalidates_get_module_query(self, mock_delete, mock_module_class):
        """Test that invalidate_module_cache invalidates getModule queries."""
        mock_module_class.objects.filter.return_value = []
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


class TestGetUserRole:
    """Test cases for the _get_user_role function."""

    @pytest.fixture
    def mock_info(self):
        """Return a mock GraphQL resolve info."""

        class MockRequest:
            """Mock request object that can store attributes."""

            def __init__(self):
                self.user = MagicMock()

        mock = MagicMock()
        mock.context.request = MockRequest()
        return mock

    def test_returns_public_for_unauthenticated_user(self, mock_info):
        """Test that _get_user_role returns 'public' for unauthenticated users."""
        mock_info.context.request.user.is_authenticated = False
        field_args = {"programKey": "test-program"}

        role = _get_user_role(mock_info, field_args)

        assert role == "public"

    def test_returns_public_when_no_program_key(self, mock_info):
        """Test that _get_user_role returns 'public' when programKey is missing."""
        mock_info.context.request.user.is_authenticated = True
        field_args = {}

        role = _get_user_role(mock_info, field_args)

        assert role == "public"

    def test_returns_public_when_user_has_no_github_user(self, mock_info):
        """Test that _get_user_role returns 'public' when user has no github_user."""
        mock_info.context.request.user.is_authenticated = True
        mock_info.context.request.user.github_user = None
        field_args = {"programKey": "test-program"}

        role = _get_user_role(mock_info, field_args)

        assert role == "public"

    @patch("apps.api.internal.extensions.cache.Mentor")
    def test_returns_public_when_user_is_not_mentor(self, mock_mentor_model, mock_info):
        """Test that _get_user_role returns 'public' when user is not a mentor."""
        mock_info.context.request.user.is_authenticated = True
        mock_info.context.request.user.github_user = MagicMock()
        mock_mentor_model.objects.filter.return_value.first.return_value = None
        field_args = {"programKey": "test-program"}

        role = _get_user_role(mock_info, field_args)

        assert role == "public"

    @patch("apps.api.internal.extensions.cache.Program")
    @patch("apps.api.internal.extensions.cache.Mentor")
    def test_returns_admin_when_user_is_program_admin(
        self, mock_mentor_model, mock_program_model, mock_info
    ):
        """Test that _get_user_role returns 'admin' when user is program admin."""
        mock_info.context.request.user.is_authenticated = True
        mock_info.context.request.user.github_user = MagicMock()
        mock_mentor = MagicMock()
        mock_mentor_model.objects.filter.return_value.first.return_value = mock_mentor
        mock_program_model.objects.filter.return_value.exists.return_value = True
        field_args = {"programKey": "test-program"}

        role = _get_user_role(mock_info, field_args)

        assert role == "admin"

    @patch("apps.api.internal.extensions.cache.Program")
    @patch("apps.api.internal.extensions.cache.Mentor")
    def test_returns_public_when_user_is_not_admin_or_mentor(
        self, mock_mentor_model, mock_program_model, mock_info
    ):
        """Test that _get_user_role returns 'public' when user is not admin or mentor."""
        mock_info.context.request.user.is_authenticated = True
        mock_info.context.request.user.github_user = MagicMock()
        mock_mentor = MagicMock()
        mock_mentor_model.objects.filter.return_value.first.return_value = mock_mentor
        mock_program_model.objects.filter.return_value.exists.return_value = False
        field_args = {"programKey": "test-program"}

        role = _get_user_role(mock_info, field_args)

        assert role == "public"

    @patch("apps.api.internal.extensions.cache.Program")
    @patch("apps.api.internal.extensions.cache.Mentor")
    def test_caches_role_on_request_object(self, mock_mentor_model, mock_program_model, mock_info):
        """Test that _get_user_role caches the role on the request object."""
        mock_info.context.request.user.is_authenticated = True
        mock_info.context.request.user.github_user = MagicMock()
        mock_mentor = MagicMock()
        mock_mentor_model.objects.filter.return_value.first.return_value = mock_mentor
        mock_program_model.objects.filter.return_value.exists.return_value = True
        field_args = {"programKey": "test-program"}

        role1 = _get_user_role(mock_info, field_args)
        assert role1 == "admin"
        assert mock_mentor_model.objects.filter.call_count == 1
        assert mock_program_model.objects.filter.call_count == 1

        role2 = _get_user_role(mock_info, field_args)
        assert role2 == "admin"
        assert mock_mentor_model.objects.filter.call_count == 1
        assert mock_program_model.objects.filter.call_count == 1

    @patch("apps.api.internal.extensions.cache.Program")
    @patch("apps.api.internal.extensions.cache.Mentor")
    def test_cache_is_keyed_by_program(self, mock_mentor_model, mock_program_model, mock_info):
        """Test that request cache is keyed by programKey."""
        mock_info.context.request.user.is_authenticated = True
        mock_info.context.request.user.github_user = MagicMock()
        mock_mentor = MagicMock()
        mock_mentor_model.objects.filter.return_value.first.return_value = mock_mentor

        mock_program_model.objects.filter.return_value.exists.return_value = True
        role1 = _get_user_role(mock_info, {"programKey": "program-1"})
        assert role1 == "admin"

        mock_program_model.objects.filter.return_value.exists.return_value = False
        role2 = _get_user_role(mock_info, {"programKey": "program-2"})
        assert role2 == "public"

        role3 = _get_user_role(mock_info, {"programKey": "program-1"})
        assert role3 == "admin"

        assert mock_program_model.objects.filter.call_count == 2

    def test_caches_public_for_unauthenticated(self, mock_info):
        """Test that public role is returned immediately for unauthenticated users."""
        mock_info.context.request.user.is_authenticated = False
        field_args = {"programKey": "test-program"}

        role1 = _get_user_role(mock_info, field_args)
        role2 = _get_user_role(mock_info, field_args)

        assert role1 == "public"
        assert role2 == "public"


class TestInvalidateCache:
    """Test cases for invalidate_cache function."""

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_deletes_cache_key(self, mock_delete):
        """Test that invalidate_cache deletes the correct cache key."""
        mock_delete.return_value = True

        result = invalidate_cache("getProgram", {"programKey": "test"}, role="admin")

        assert result is True
        mock_delete.assert_called_once()

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_returns_false_when_key_not_found(self, mock_delete):
        """Test that invalidate_cache returns False when key doesn't exist."""
        mock_delete.return_value = False

        result = invalidate_cache("getProgram", {"programKey": "test"}, role="admin")

        assert result is False

    @patch("apps.api.internal.extensions.cache.cache.delete")
    def test_handles_none_role(self, mock_delete):
        """Test that invalidate_cache handles None role correctly."""
        mock_delete.return_value = True

        result = invalidate_cache("someField", {"key": "value"}, role=None)

        assert result is True
        expected_key = generate_key("someField", {"key": "value"}, None)
        mock_delete.assert_called_once_with(expected_key)


class TestCacheExtensionAdvanced:
    """Advanced test cases for CacheExtension resolve method."""

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
        mock.field_name = "getProgram"
        mock.parent_type.name = "Query"
        mock.context.request.user = MagicMock()
        mock.context.request.user.is_authenticated = True
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

    @patch("apps.api.internal.extensions.cache._get_user_role")
    @patch("apps.api.internal.extensions.cache.cache")
    def test_uses_role_for_role_aware_fields(
        self, mock_cache, mock_get_user_role, extension, mock_info, mock_next
    ):
        """Test that role-aware fields use _get_user_role to determine cache key."""
        mock_get_user_role.return_value = "admin"
        mock_cache.get.return_value = CACHE_MISS
        mock_info.field_name = "getProgram"

        extension.resolve(mock_next, None, mock_info, programKey="test")

        mock_get_user_role.assert_called_once()
        assert mock_cache.get.call_count == 1

    @patch("apps.api.internal.extensions.cache.cache")
    def test_does_not_cache_coroutines(self, mock_cache, extension, mock_info):
        """Test that async coroutines are not cached."""

        async def async_resolver():
            await asyncio.sleep(0)
            return {"name": "Async OWASP"}

        mock_next = MagicMock(return_value=async_resolver())
        mock_cache.get.return_value = CACHE_MISS
        mock_info.field_name = "chapter"

        result = extension.resolve(mock_next, None, mock_info, key="test")

        assert asyncio.iscoroutine(result)
        mock_cache.set.assert_not_called()
        result.close()

    @patch("apps.api.internal.extensions.cache.cache")
    def test_converts_queryset_to_list(self, mock_cache, extension, mock_info, mock_next):
        """Test that QuerySet results are converted to list before caching."""
        mock_queryset = MagicMock(spec=QuerySet)
        mock_next.return_value = mock_queryset
        mock_cache.get.return_value = CACHE_MISS
        mock_info.field_name = "chapter"

        extension.resolve(mock_next, None, mock_info, key="test")

        mock_cache.set.assert_called_once()

    def test_role_aware_fields_includes_all_expected_fields(self):
        """Test that ROLE_AWARE_FIELDS includes all expected fields."""
        assert "getProgram" in CacheExtension.ROLE_AWARE_FIELDS
        assert "getProgramModules" in CacheExtension.ROLE_AWARE_FIELDS
        assert "getModule" in CacheExtension.ROLE_AWARE_FIELDS

    @patch("apps.api.internal.extensions.cache.cache")
    def test_cache_miss_sentinel_allows_caching_none(
        self, mock_cache, extension, mock_info, mock_next
    ):
        """Test that CACHE_MISS sentinel allows caching None values."""
        mock_cache.get.return_value = CACHE_MISS
        mock_next.return_value = None
        mock_info.field_name = "chapter"

        result = extension.resolve(mock_next, None, mock_info, key="test")

        assert result is None
        mock_cache.set.assert_called_once()
        cached_value = mock_cache.set.call_args[0][1]
        assert cached_value is None
