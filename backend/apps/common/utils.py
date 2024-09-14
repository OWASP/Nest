"""Common app utils."""

from django.conf import settings
from django.urls import reverse


def get_absolute_url(view_name):
    """Return absolute URL for a view."""
    return f"{settings.SITE_URL}{reverse(view_name)}"


def join_values(fields, delimiter=" "):
    """Join non-empty field values using the delimiter."""
    delimiter.join(field for field in fields if field)
