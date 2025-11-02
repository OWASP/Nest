"""Strawberry extensions."""

import json
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from strawberry.extensions.field_extension import FieldExtension
from strawberry.types.info import Info


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

    def _convert_path_to_str(self, path: Any) -> str:
        """Convert the Strawberry path linked list to a string."""
        parts = []
        current = path
        while current:
            parts.append(str(current.key))
            current = getattr(current, "prev", None)
        return ".".join(reversed(parts))

    def generate_key(self, source: Any | None, info: Info, kwargs: dict) -> str:
        """Generate a unique cache key for a field.

        Args:
            source (Any | None): The source/parent object.
            info (Info): The Strawberry execution info.
            kwargs (dict): The resolver's arguments.

        Returns:
            str: The unique cache key.

        """
        key_kwargs = kwargs.copy()
        if source and (source_id := getattr(source, "id", None)) is not None:
            key_kwargs["__source_id__"] = str(source_id)

        args_str = json.dumps(key_kwargs, sort_keys=True, cls=DjangoJSONEncoder)

        return f"{self.prefix}:{self._convert_path_to_str(info.path)}:{args_str}"

    def resolve(self, next_: Any, source: Any, info: Info, **kwargs: Any) -> Any:
        """Wrap the resolver to provide caching."""
        cache_key = self.generate_key(source, info, kwargs)

        return cache.get_or_set(
            cache_key,
            lambda: next_(source, info, **kwargs),
            timeout=self.cache_timeout,
        )
