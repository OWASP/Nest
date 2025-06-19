"""Common app utils."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.utils.text import Truncator
from django.utils.text import slugify as django_slugify
from humanize import intword, naturaltime


def convert_to_camel_case(text: str) -> str:
    """Convert a string to camelCase.

    Args:
        text (str): The input string.

    Returns:
        str: The converted string in camelCase.

    """
    parts = text.split("_")
    offset = 1 if text.startswith("_") else 0
    head = parts[offset : offset + 1] or [text]

    segments = [f"_{head[0]}" if offset else head[0]]
    segments.extend(word.capitalize() for word in parts[offset + 1 :])

    return "".join(segments)


def convert_to_snake_case(text: str) -> str:
    """Convert a string to snake_case.

    Args:
        text (str): The input string.

    Returns:
        str: The converted string in snake_case.

    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def get_absolute_url(path: str) -> str:
    """Return the absolute URL for a given path.

    Args:
        path (str): The relative path.

    Returns:
        str: The absolute URL.

    """
    return f"{settings.SITE_URL}/{path}"


def get_nest_user_agent() -> str:
    """Return the user agent string for the Nest application.

    Returns
        str: The user agent string.

    """
    return settings.APP_NAME.replace(" ", "-").lower()


def get_user_ip_address(request) -> str:
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


def join_values(fields: list, delimiter: str = " ") -> str:
    """Join non-empty field values using a specified delimiter.

    Args:
        fields (list): A list of field values.
        delimiter (str, optional): The delimiter to use.

    Returns:
        str: The joined string.

    """
    return delimiter.join(field for field in fields if field)


def natural_date(value: int | str) -> str:
    """Convert a date or timestamp into a human-readable format.

    Args:
        value (str or int or datetime): The date or timestamp to convert.

    Returns:
        str: The humanized date string.

    """
    if isinstance(value, str):
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
    elif isinstance(value, int):
        dt = datetime.fromtimestamp(value, tz=UTC)
    else:
        dt = value

    return naturaltime(dt)


def natural_number(value: int, unit=None) -> str:
    """Convert a number into a human-readable format.

    Args:
        value (int): The number to convert.
        unit (str, optional): The unit to append.

    Returns:
        str: The humanized number string.

    """
    number = intword(value)
    return f"{number} {unit}{pluralize(value)}" if unit else number


def round_down(value: int, base: int) -> int:
    """Round down the stats to the nearest base.

    Args:
        value: The value to round down.
        base: The base to round down to.

    Returns:
        int: The rounded down value.

    """
    return value - (value % base)


def slugify(text: str) -> str:
    """Generate a slug from the given text.

    Args:
        text (str): The text to slugify.

    Returns:
        str: The slugify text.

    """
    return re.sub(r"-{2,}", "-", django_slugify(text))


def truncate(text: str, limit: int, truncate: str = "...") -> str:
    """Truncate text to a specified character limit.

    Args:
        text (str): The text to truncate.
        limit (int): The character limit.
        truncate (str, optional): The truncation suffix.

    Returns:
        str: The truncated text.

    """
    return Truncator(text).chars(limit, truncate=truncate)
