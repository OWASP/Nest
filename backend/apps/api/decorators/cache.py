"""Decorator for API Cache."""

from functools import wraps
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest


def generate_key(
    request: HttpRequest,
    prefix: str,
):
    """Generate a cache key for a request."""
    return f"{prefix}:{request.get_full_path()}"


def cache_response(
    ttl: int | None = None,
    prefix: str | None = None,
):
    """Cache API responses for GET and HEAD requests.

    Args:
        ttl (int): The time-to-live for the cache entry in seconds.
        prefix (str): A prefix for the cache key.

    """
    if ttl is None:
        ttl = settings.API_CACHE_TIME_SECONDS

    if prefix is None:
        prefix = settings.API_CACHE_PREFIX

    def decorator(view_func):
        @wraps(view_func)
        def _wrapper(request, *args, **kwargs):
            if request.method not in ("GET", "HEAD"):
                return view_func(request, *args, **kwargs)

            cache_key = generate_key(
                request=request,
                prefix=prefix,
            )
            if response := cache.get(cache_key):
                return response

            response = view_func(request, *args, **kwargs)
            if response.status_code == HTTPStatus.OK:
                cache.set(cache_key, response, timeout=ttl)
            return response

        return _wrapper

    return decorator
