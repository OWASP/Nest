"""Staff utility functions for OWASP."""

import logging
from functools import lru_cache

import requests
import yaml
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


@lru_cache
def get_staff_data(timeout: float | None = 30) -> list | None:
    """Get staff data.

    Args:
        timeout: The request timeout in seconds.

    Returns:
        A sorted list of staff data dictionaries, or None if an error occurs.

    """
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
        return None
