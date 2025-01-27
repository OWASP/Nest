"""Slack app utils."""

import html
from functools import lru_cache

import requests
import yaml

from apps.slack.constants import OWASP_STAFF_DATA_URL


def escape(content):
    """Escape HTML content."""
    return html.escape(content, quote=False)


@lru_cache(maxsize=1)
def get_staff_data(timeout=30):
    """Get Staff content."""
    return yaml.safe_load(requests.get(OWASP_STAFF_DATA_URL, timeout=timeout).text)
