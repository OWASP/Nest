"""Custom template filters for URL sanitization."""

from django import template

from apps.common.utils import validate_url

register = template.Library()


@register.filter
def safe_url(url):
    """Return the URL only if it has a safe scheme (http/https), otherwise return '#'.

    This prevents XSS attacks via javascript: URIs in anchor href attributes.
    """
    return url if validate_url(url) else "#"
