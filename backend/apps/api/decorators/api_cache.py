"""Decorator for API Cache."""

from functools import wraps
from http import HTTPStatus
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest


def _generate_cache_key(
    request: HttpRequest,
    allowed_params: tuple[str, ...] | None,
    prefix: str,
):
    """Generate a cache key for a request."""
    parts = [prefix, request.path]

    if request.GET and allowed_params:
        filtered_params = {
            key: value for key, value in request.GET.items() if key in allowed_params
        }
        if filtered_params:
            parts.append(urlencode(sorted(filtered_params.items())))

    return ":".join(parts)


def cache_api_response(
    ttl: int | None = None,
    allowed_params: tuple[str, ...] | None = None,
    prefix: str | None = None,
):
    """Cache API responses for GET and HEAD requests.

    Args:
        ttl (int): The time-to-live for the cache entry in seconds.
        allowed_params: A tuple of query parameter names that should be included in the cache key.
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

            cache_key = _generate_cache_key(
                request=request,
                allowed_params=allowed_params,
                prefix=prefix,
            )

            if response := cache.get(cache_key):
                return response

            response = view_func(request, *args, **kwargs)
            if HTTPStatus.OK <= response.status_code < HTTPStatus.MULTIPLE_CHOICES:
                cache.set(cache_key, response, timeout=ttl)
            return response

        return _wrapper

    return decorator
