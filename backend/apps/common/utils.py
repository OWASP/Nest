"""Common app utils."""

import re
from datetime import datetime, timezone

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.utils.text import Truncator
from django.utils.text import slugify as django_slugify
from humanize import intword, naturaltime


def get_absolute_url(path):
    """Return the absolute URL for a given path.

    Args:
        path (str): The relative path.

    Returns:
        str: The absolute URL.

    """
    return f"{settings.SITE_URL}/{path}"


def get_nest_user_agent():
    """Return the user agent string for the Nest application.

    Returns
        str: The user agent string.

    """
    return settings.APP_NAME.replace(" ", "-").lower()


def get_user_ip_address(request):
    """Retrieve the user's IP address from the request.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        str: The user's IP address.

    """
    if settings.ENVIRONMENT == "Local":
        return settings.PUBLIC_IP_ADDRESS

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


def join_values(fields, delimiter=" "):
    """Join non-empty field values using a specified delimiter.

    Args:
        fields (list): A list of field values.
        delimiter (str, optional): The delimiter to use.

    Returns:
        str: The joined string.

    """
    return delimiter.join(field for field in fields if field)


def natural_date(value):
    """Convert a date or timestamp into a human-readable format.

    Args:
        value (str or int or datetime): The date or timestamp to convert.

    Returns:
        str: The humanized date string.

    """
    if isinstance(value, str):
        value = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    elif isinstance(value, int):
        value = datetime.fromtimestamp(value, tz=timezone.utc)

    return naturaltime(value)


def natural_number(value, unit=None):
    """Convert a number into a human-readable format.

    Args:
        value (int): The number to convert.
        unit (str, optional): The unit to append.

    Returns:
        str: The humanized number string.

    """
    number = intword(value)
    return f"{number} {unit}{pluralize(value)}" if unit else number


def slugify(text):
    """Generate a slug from the given text.

    Args:
        text (str): The text to slugify.

    Returns:
        str: The slugify text.

    """
    return re.sub(r"-{2,}", "-", django_slugify(text))


def truncate(text, limit, truncate="..."):
    """Truncate text to a specified character limit.

    Args:
        text (str): The text to truncate.
        limit (int): The character limit.
        truncate (str, optional): The truncation suffix.

    Returns:
        str: The truncated text.

    """
    return Truncator(text).chars(limit, truncate=truncate)
