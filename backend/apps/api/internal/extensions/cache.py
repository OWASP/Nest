"""Strawberry cache extension."""

import hashlib
import json
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from strawberry.extensions import SchemaExtension
from strawberry.permission import PermissionExtension
from strawberry.schema import Schema
from strawberry.utils.str_converters import to_camel_case


@lru_cache(maxsize=1)
def get_protected_fields(schema: Schema) -> tuple[str, ...]:
    """Get protected field names.

    Args:
        schema (Schema): The GraphQL schema.

    Returns:
        tuple[str, ...]: Tuple of protected field names in camelCase.

    """
    return tuple(
        to_camel_case(field.name)
        for field in getattr(
            getattr(schema.schema_converter.type_map.get("Query"), "definition", None),
            "fields",
            (),
        )
        if any(isinstance(ext, PermissionExtension) for ext in field.extensions)
    )


def generate_key(field_name: str, field_args: dict) -> str:
    """Generate a unique cache key for a query.

    Args:
        field_name (str): The GraphQL field name.
        field_args (dict): The field's arguments.

    Returns:
        str: The unique cache key.

    """
    key = f"{field_name}:{json.dumps(field_args, cls=DjangoJSONEncoder, sort_keys=True)}"
    return f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-{hashlib.sha256(key.encode()).hexdigest()}"


def invalidate_cache(field_name: str, field_args: dict) -> bool:
    """Invalidate a specific GraphQL query from the resolver cache.

    Args:
        field_name: The GraphQL field name (e.g., 'getProgram').
        field_args: The field's arguments as a dict (e.g., {'programKey': 'my-program'}).

    Returns:
        True if cache was invalidated, False if key didn't exist.

    """
    return cache.delete(generate_key(field_name, field_args))


def invalidate_program_cache(program_key: str) -> None:
    """Invalidate all GraphQL caches related to a program.

    Args:
        program_key: The program's key identifier.

    """
    invalidate_cache("getProgram", {"programKey": program_key})
    invalidate_cache("getProgramModules", {"programKey": program_key})


def invalidate_module_cache(module_key: str, program_key: str) -> None:
    """Invalidate all GraphQL caches related to a module.

    Args:
        module_key: The module's key identifier.
        program_key: The program's key identifier.

    """
    invalidate_cache("getModule", {"moduleKey": module_key, "programKey": program_key})
    invalidate_program_cache(program_key)


class CacheExtension(SchemaExtension):
    """Cache extension."""

    def resolve(self, _next, root, info, *args, **kwargs):
        """Wrap the resolver to provide caching."""
        if (
            info.field_name.startswith("__")
            or info.parent_type.name != "Query"
            or info.field_name in get_protected_fields(self.execution_context.schema)
        ):
            return _next(root, info, *args, **kwargs)

        return cache.get_or_set(
            generate_key(info.field_name, kwargs),
            lambda: _next(root, info, *args, **kwargs),
            settings.GRAPHQL_RESOLVER_CACHE_TIME_SECONDS,
        )
