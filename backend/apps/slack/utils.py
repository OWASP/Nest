"""Slack app utils."""

import html
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def escape(content):
    """Escape HTML content."""
    return html.escape(content, quote=False)


def send_to_analytics(query, command):
    """Send the search query to the analytics endpoint."""
    analytics_url = f"{settings.SITE_URL}/api/v1/analytics/search/"
    payload = {"query": query, "source": "nestbot", "category": command.strip("/")}
    try:
        response = requests.post(analytics_url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception("Failed to send analytics data")
