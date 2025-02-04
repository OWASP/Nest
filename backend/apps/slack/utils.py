"""Slack app utils."""

import html
import logging
from functools import lru_cache

import graphene
import requests
import yaml
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


def escape(content):
    """Escape HTML content."""
    return html.escape(content, quote=False)


@lru_cache
def get_staff_data(timeout=30):
    """Get staff data."""
    file_path = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/staff.yml"
    try:
        return sorted(
            yaml.safe_load(
                requests.get(
                    file_path,
                    timeout=timeout,
                ).text
            ),
            key=lambda p: p["name"],
        )
    except (RequestException, yaml.scanner.ScannerError):
        logger.exception("Unable to parse OWASP staff data file", extra={"file_path": file_path})


def get_events_data():
    """Get raw events data via GraphQL."""
    from apps.owasp.graphql.queries.event import EventQuery

    query = """
    query {
        events {
            key
            name
            category
            dates
            startDate
            url
            optionalText
            description
            categoryDescription
        }
    }
    """
    try:
        result = graphene.Schema(query=EventQuery).execute(query)
        return result.data["events"]
    except Exception as e:
        logger.exception("Failed to fetch events data via GraphQL", extra={"error": str(e)})
        return None
