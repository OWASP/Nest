"""Strawberry extensions."""

import json

from django.conf import settings
from django.core.cache import cache
from strawberry.extensions.field_extension import FieldExtension


class CacheFieldExtension(FieldExtension):
    """Cache FieldExtension class."""

    def __init__(self, cache_timeout: int | None = None, prefix: str | None = None):
        """Initialize the cache extension.

        Args:
            cache_timeout (int | None): The TTL for cache entries in seconds.
            prefix (str | None): A prefix for the cache key.

        """
        self.cache_timeout = cache_timeout or settings.GRAPHQL_RESOLVER_CACHE_TIME_SECONDS
        self.prefix = prefix or settings.GRAPHQL_RESOLVER_CACHE_PREFIX

    def generate_key(self, info, kwargs: dict) -> str:
        """Generate a unique cache key for a field.

        Args:
            info (Info): The Strawberry execution info.
            kwargs (dict): The resolver's arguments.

        Returns:
            str: The unique cache key.

        """
        args_str = json.dumps(kwargs, sort_keys=True)

        return f"{self.prefix}:{info.path.typename}:{info.path.key}:{args_str}"

    def resolve(self, next_, source, info, **kwargs):
        """Wrap the resolver to provide caching."""
        cache_key = self.generate_key(info, kwargs)
        if cached_result := cache.get(cache_key):
            return cached_result

        if result := next_(source, info, **kwargs):
            cache.set(cache_key, result, self.cache_timeout)

        return result
