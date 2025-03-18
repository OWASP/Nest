"""Common app utils."""

import re
from datetime import datetime, timezone

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.utils.text import Truncator
from django.utils.text import slugify as django_slugify
from humanize import intword, naturaltime


def get_absolute_url(path):
    """Return absolute URL for a view."""
    return f"{settings.SITE_URL}/{path}"


def get_nest_user_agent():
    """Return Nest user agent."""
    return settings.APP_NAME.replace(" ", "-").lower()


def get_user_ip_address(request):
    """Return user's IP address."""
    if settings.ENVIRONMENT == "Local":
        return settings.PUBLIC_IP_ADDRESS

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


def join_values(fields, delimiter=" "):
    """Join non-empty field values using the delimiter."""
    return delimiter.join(field for field in fields if field)


def natural_date(value):
    """Return humanized version of a date."""
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    elif isinstance(value, int):
        value = datetime.fromtimestamp(value, tz=timezone.utc)

    return naturaltime(value)


def natural_number(value, unit=None):
    """Return humanized version of a number."""
    number = intword(value)
    return f"{number} {unit}{pluralize(value)}" if unit else number


def slugify(text):
    """Return slug for text."""
    return re.sub(r"-{2,}", "-", django_slugify(text))


def truncate(text, limit, truncate="..."):
    """Truncate text to the given limit."""
    return Truncator(text).chars(limit, truncate=truncate)
