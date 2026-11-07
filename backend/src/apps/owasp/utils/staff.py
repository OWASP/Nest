"""Staff utility functions for OWASP."""

import logging

import requests
import yaml
from django.core.cache import cache
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)
CACHE_TTL_SECONDS = 30 * 60
STAFF_CACHE_KEY = "slack:staff_data"
STAFF_YAML_URL = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/staff.yml"


def is_valid_staff_data(data: object) -> bool:
    """Return True when staff YAML parses to a list of dicts with name keys."""
    if not isinstance(data, list):
        return False
    return all(isinstance(person, dict) and "name" in person for person in data)


def get_staff_data(timeout: float | None = 30) -> list | None:
    """Get staff data.

    Args:
        timeout (float, optional): The request timeout in seconds.

    Returns:
        list or None: A sorted list of staff data dictionaries, or None if an error occurs.

    """
    cache_key = f"{STAFF_CACHE_KEY}:{timeout}"
    if (cached := cache.get(cache_key)) is not None:
        return cached

    try:
        response = requests.get(STAFF_YAML_URL, timeout=timeout)
        response.raise_for_status()
        data = yaml.safe_load(response.text)
        if not is_valid_staff_data(data):
            logger.error(
                "Unable to parse OWASP staff data file",
                extra={"file_path": STAFF_YAML_URL},
            )
            return None

        result = sorted(data, key=lambda person: person["name"])
        cache.set(cache_key, result, timeout=CACHE_TTL_SECONDS)
    except RequestException:
        logger.exception(
            "Unable to fetch OWASP staff data file", extra={"file_path": STAFF_YAML_URL}
        )
        return None
    except (AttributeError, KeyError, TypeError, yaml.YAMLError):
        logger.exception(
            "Unable to parse OWASP staff data file", extra={"file_path": STAFF_YAML_URL}
        )
        return None
    else:
        return result
