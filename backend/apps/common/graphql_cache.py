"""GraphQL cache utilities for invalidating cached queries."""

import hashlib
import json
import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def invalidate_graphql_cache(field_name: str, field_args: dict) -> bool:
    """Invalidate a specific GraphQL query from the resolver cache.

    Args:
        field_name: The GraphQL field name (e.g., 'getProgram').
        field_args: The field's arguments as a dict (e.g., {'programKey': 'my-program'}).

    Returns:
        True if cache was invalidated, False if key didn't exist.
    """
    key = f"{field_name}:{json.dumps(field_args, sort_keys=True)}"
    cache_key = f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-{hashlib.sha256(key.encode()).hexdigest()}"
    result = cache.delete(cache_key)
    return result


def invalidate_program_cache(program_key: str) -> None:
    """Invalidate all GraphQL caches related to a program.

    Args:
        program_key: The program's key identifier.
    """
    invalidate_graphql_cache("getProgram", {"programKey": program_key})

    invalidate_graphql_cache("getProgramModules", {"programKey": program_key})


def invalidate_module_cache(program_key: str, module_key: str) -> None:
    """Invalidate all GraphQL caches related to a module.

    Args:
        program_key: The program's key identifier.
        module_key: The module's key identifier.
    """

    invalidate_graphql_cache("getModule", {"moduleKey": module_key, "programKey": program_key})

    invalidate_program_cache(program_key)
