"""Strawberry extensions."""

import hashlib
import json
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from strawberry.extensions import SchemaExtension
from strawberry.permission import PermissionExtension
from strawberry.schema import Schema
from strawberry.utils.str_converters import to_camel_case

CACHE_VERSION_KEY = "graphql:cache_version"


def get_cache_version() -> int:
    """Get the current cache version."""
    return cache.get_or_set(CACHE_VERSION_KEY, 1, timeout=None)


def bump_cache_version() -> None:
    """Bump the cache version."""
    try:
        cache.incr(CACHE_VERSION_KEY)
    except ValueError:
        cache.set(CACHE_VERSION_KEY, 2)


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


class CacheExtension(SchemaExtension):
    """CacheExtension class."""

    def generate_key(self, field_name: str, field_args: dict) -> str:
        """Generate a unique cache key for a query.

        Args:
            field_name (str): The GraphQL field name.
            field_args (dict): The field's arguments.

        Returns:
            str: The unique cache key.

        """
        version = get_cache_version()
        key = (
            f"{field_name}:{json.dumps({'args': field_args, 'version': version}, sort_keys=True)}"
        )
        return (
            f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-{hashlib.sha256(key.encode()).hexdigest()}"
        )

    def resolve(self, _next, root, info, *args, **kwargs):
        """Wrap the resolver to provide caching."""
        if (
            info.field_name.startswith("__")
            or info.parent_type.name != "Query"
            or info.field_name in get_protected_fields(self.execution_context.schema)
        ):
            return _next(root, info, *args, **kwargs)

        return cache.get_or_set(
            self.generate_key(info.field_name, kwargs),
            lambda: _next(root, info, *args, **kwargs),
            settings.GRAPHQL_RESOLVER_CACHE_TIME_SECONDS,
        )


class CacheInvalidationExtension(SchemaExtension):
    """CacheInvalidationExtension class."""

    def on_execute(self):
        """Invalidate cache on mutation."""
        if str(self.execution_context.operation_type) == "OperationType.MUTATION":
            bump_cache_version()
