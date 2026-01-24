"""Strawberry cache extension."""

import asyncio
import hashlib
import json
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, QuerySet
from strawberry.extensions import SchemaExtension
from strawberry.permission import PermissionExtension
from strawberry.schema import Schema
from strawberry.utils.str_converters import to_camel_case

from apps.mentorship.models import Program
from apps.mentorship.models.mentor import Mentor


@lru_cache(maxsize=1)
def get_protected_fields(schema: Schema) -> tuple[str, ...]:
    """Get protected field names.

    Args:
        schema (Schema): The GraphQL schema.

    Returns:
        tuple[str, ...]: Tuple of protected field names in camelCase.

    """
    query_type = schema.schema_converter.type_map.get("Query")
    fields = getattr(getattr(query_type, "definition", None), "fields", ())
    return tuple(
        to_camel_case(field.name)
        for field in fields
        if any(isinstance(ext, PermissionExtension) for ext in field.extensions)
    )


CACHE_MISS = object()


def _get_user_role(info, field_args: dict) -> str:
    """Determine user role.

    Args:
        info: GraphQL resolver info.
        field_args: Query arguments (may contain programKey).

    Returns:
        str: 'admin' or 'public'

    """
    user = getattr(info.context.request, "user", None)
    program_key = field_args.get("programKey")

    if not user or not user.is_authenticated or not program_key:
        return "public"

    github_user = getattr(user, "github_user", None)
    mentor = Mentor.objects.filter(github_user=github_user).first() if github_user else None
    if not mentor:
        return "public"

    is_admin_or_mentor = Program.objects.filter(
        Q(key=program_key) & (Q(admins=mentor) | Q(modules__mentors=mentor))
    ).exists()

    return "admin" if is_admin_or_mentor else "public"


def generate_key(field_name: str, field_args: dict, role: str | None = None) -> str:
    """Generate a unique cache key for a query.

    Args:
        field_name (str): The GraphQL field name.
        field_args (dict): The field's arguments.
        role (str | None): User role ('admin' or 'public') for role-aware fields.

    Returns:
        str: The unique cache key.

    """
    cache_data = {"field": field_name, "args": field_args, "role": role}
    key = json.dumps(cache_data, cls=DjangoJSONEncoder, sort_keys=True)
    return f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-{hashlib.sha256(key.encode()).hexdigest()}"


def invalidate_cache(field_name: str, field_args: dict, role: str | None = None) -> bool:
    """Invalidate a specific GraphQL query from the resolver cache.

    Args:
        field_name: The GraphQL field name (e.g., 'getProgram').
        field_args: The field's arguments as a dict (e.g., {'programKey': 'my-program'}).
        role: User role ('admin' or 'public') for role-aware fields.

    Returns:
        True if cache was invalidated, False if key didn't exist.

    """
    return cache.delete(generate_key(field_name, field_args, role))


def invalidate_program_cache(program_key: str) -> None:
    """Invalidate all GraphQL caches related to a program.

    Args:
        program_key: The program's key identifier.

    """
    for role in ["admin", "public"]:
        invalidate_cache("getProgram", {"programKey": program_key}, role)
        invalidate_cache("getProgramModules", {"programKey": program_key}, role)


def invalidate_module_cache(module_key: str, program_key: str) -> None:
    """Invalidate all GraphQL caches related to a module.

    Args:
        module_key: The module's key identifier.
        program_key: The program's key identifier.

    """
    for role in ["admin", "public"]:
        invalidate_cache("getModule", {"moduleKey": module_key, "programKey": program_key}, role)
    invalidate_program_cache(program_key)


class CacheExtension(SchemaExtension):
    """Cache extension with role-aware caching."""

    ROLE_AWARE_FIELDS = ("getProgram", "getProgramModules", "getModule")

    def resolve(self, _next, root, info, *args, **kwargs):
        """Wrap the resolver to provide role-aware caching."""
        if (
            info.field_name.startswith("__")
            or info.parent_type.name != "Query"
            or info.field_name in get_protected_fields(self.execution_context.schema)
        ):
            return _next(root, info, *args, **kwargs)

        role = None
        if info.field_name in self.ROLE_AWARE_FIELDS:
            role = _get_user_role(info, kwargs)

        cache_key = generate_key(info.field_name, kwargs, role)
        cached_result = cache.get(cache_key, CACHE_MISS)
        if cached_result is not CACHE_MISS:
            return cached_result

        result = _next(root, info, *args, **kwargs)

        if asyncio.iscoroutine(result):
            return result

        if isinstance(result, QuerySet):
            result = list(result)

        cache.set(cache_key, result, settings.GRAPHQL_RESOLVER_CACHE_TIME_SECONDS)
        return result
