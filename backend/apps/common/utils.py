"""Utility helper functions used across the common app."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.utils.text import Truncator
from django.utils.text import slugify as django_slugify
from humanize import intword, naturaltime

if TYPE_CHECKING:
    from django.http import HttpRequest


def convert_to_camel_case(text: str) -> str:
    """Convert a snake_case string into camelCase format.

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
    """Convert a camelCase or PascalCase string into snake_case format.

    Args:
        text (str): The input string.

    Returns:
        str: The converted string in snake_case.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", text).lower()


def clean_url(url: str | None) -> str | None:
    """Clean a URL string by trimming whitespace and trailing punctuation.

    Args:
        url (str, optional): Raw URL string.

    Returns:
        str | None: Cleaned URL string or None if empty.
    """
    if not url:
        return None

    return url.strip().rstrip(".,;:!?") or None


def get_absolute_url(path: str) -> str:
    """Build an absolute URL using the site's base URL and a given path.

    Args:
        path (str): The relative path.

    Returns:
        str: The complete absolute URL.
    """
    return f"{settings.SITE_URL}/{path.lstrip('/')}"


def get_nest_user_agent() -> str:
    """Generate the user agent string for the Nest application.

    Returns:
        str: The formatted user agent string.
    """
    return settings.APP_NAME.replace(" ", "-").lower()


def get_user_ip_address(request: HttpRequest) -> str:
    """Get the client's IP address from the HTTP request.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        str: The client's IP address.
    """
    if settings.IS_LOCAL_ENVIRONMENT or settings.IS_E2E_ENVIRONMENT:
        return settings.PUBLIC_IP_ADDRESS

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


def is_valid_json(content: str) -> bool:
    """Check whether the given string contains valid JSON data.

    Args:
        content (str): The content string to validate.

    Returns:
        bool: True if content is valid JSON, otherwise False.
    """
    try:
        json.loads(content)
    except (TypeError, ValueError):
        return False
    return True


def join_values(fields: list, delimiter: str = " ") -> str:
    """Join non-empty values from a list using a chosen delimiter.

    Args:
        fields (list): A list of field values.
        delimiter (str, optional): The delimiter to use. Defaults to " ".

    Returns:
        str: A single joined string.
    """
    return delimiter.join(field for field in fields if field)


def natural_date(value: int | str | datetime) -> str:
    """Convert a date, timestamp, or datetime into a human-readable relative time.

    Args:
        value (int | str | datetime): The date or timestamp to convert.

    Returns:
        str: The human-friendly date string.
    """
    if isinstance(value, str):
        dt = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=UTC)
    elif isinstance(value, int):
        dt = datetime.fromtimestamp(value, tz=UTC)
    else:
        dt = value

    return naturaltime(dt)


def natural_number(value: int, unit: str | None = None) -> str:
    """Convert a number into a shorter, human-readable format.

    Args:
        value (int): The number to convert.
        unit (str, optional): The unit to append.

    Returns:
        str: The formatted number string.
    """
    number = intword(value)
    return f"{number} {unit}{pluralize(value)}" if unit else number


def round_down(value: int, base: int) -> int:
    """Round a number down to the nearest multiple of the given base.

    Args:
        value (int): The value to round down.
        base (int): The base multiple.

    Returns:
        int: The rounded down value.
    """
    return value - (value % base)


def slugify(text: str) -> str:
    """Convert text into a URL-friendly slug.

    Args:
        text (str): The text to slugify.

    Returns:
        str: The generated slug string.
    """
    return re.sub(r"-{2,}", "-", django_slugify(text))


def truncate(text: str, limit: int, truncate: str = "...") -> str:
    """Shorten text to a specified character limit.

    Args:
        text (str): The text to truncate.
        limit (int): The character limit.
        truncate (str, optional): The suffix added after truncation. Defaults to "...".

    Returns:
        str: The shortened text.
    """
    return Truncator(text).chars(limit, truncate=truncate)


def normalize_limit(limit: int, max_limit: int = 1000) -> int | None:
    """Validate and normalize a limit value within allowed bounds.

    Args:
        limit (int): The requested limit.
        max_limit (int): The maximum allowed limit. Defaults to 1000.

    Returns:
        int | None: The adjusted limit, or None if invalid.
    """
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        return None

    if limit <= 0:
        return None

    return min(limit, max_limit)


def validate_url(url: str | None) -> bool:
    """Check whether a URL is valid and properly structured.

    Args:
        url (str, optional): URL string to validate.

    Returns:
        bool: True if the URL is valid, otherwise False.
    """
    max_url_length = 2048
    if (
        not url
        or len(url) > max_url_length
        or re.search(r"[\x00-\x1f\x7f]", url)
    ):
        return False

    try:
        parsed = urlparse(url)

        min_port = 1
        max_port = 65535
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or not re.search(r"[a-zA-Z0-9]", parsed.netloc)
            or not (hostname := parsed.hostname)
            or hostname.startswith((".", "-"))
            or hostname.endswith("-")
            or (parsed.port is not None and not (min_port <= parsed.port <= max_port))
        ):
            return False
    except ValueError:
        return False

    return True