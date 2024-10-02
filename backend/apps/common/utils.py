"""Common app utils."""

from datetime import datetime, timezone

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.urls import reverse
from humanize import intword, naturaltime


def get_absolute_url(view_name):
    """Return absolute URL for a view."""
    return f"{settings.SITE_URL}{reverse(view_name)}"


def get_nest_user_agent():
    """Return Nest user agent."""
    return settings.APP_NAME.replace(" ", "-").lower()


def join_values(fields, delimiter=" "):
    """Join non-empty field values using the delimiter."""
    return delimiter.join(field for field in fields if field)


def natural_date(value):
    """Return humanized version of a date."""
    return naturaltime(datetime.fromtimestamp(value, tz=timezone.utc))


def natural_number(value, unit=None):
    """Return humanized version of a number."""
    number = intword(value)
    return f"{number} {unit}{pluralize(value)}" if unit else number
