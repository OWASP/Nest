"""Strawberry extensions."""

import hashlib
import json

from django.conf import settings
from django.core.cache import cache
from graphql import OperationType
from strawberry.extensions import SchemaExtension
from strawberry.types import ExecutionContext


class CacheExtension(SchemaExtension):
    """CacheExtension class."""

    def generate_key(self, execution_context: ExecutionContext) -> str:
        """Generate a unique cache key for a query.

        Args:
            execution_context (ExecutionContext): The execution context.

        Returns:
            str: The unique cache key.

        """
        key = f"{execution_context.query}:{json.dumps(execution_context.variables)}"
        return (
            f"{settings.GRAPHQL_RESOLVER_CACHE_PREFIX}-{hashlib.sha256(key.encode()).hexdigest()}"
        )

    def should_skip_cache(self, execution_context: ExecutionContext) -> bool:
        """Check if caching should be skipped for this request.

        Args:
            execution_context (ExecutionContext): The execution context.

        Returns:
            bool: True if caching should be skipped.

        """
        if execution_context.operation_type != OperationType.QUERY:
            return True

        request = execution_context.context.request
        return hasattr(request, "user") and request.user.is_authenticated

    def on_execute(self):
        """Wrap the resolver to provide caching."""
        if self.should_skip_cache(self.execution_context):
            yield
            return

        cache_key = self.generate_key(self.execution_context)
        if cached_response := cache.get(cache_key):
            self.execution_context.result = cached_response
            yield
            return

        yield
        result = self.execution_context.result
        cache.set(cache_key, result, settings.GRAPHQL_RESOLVER_CACHE_TIME_SECONDS)
