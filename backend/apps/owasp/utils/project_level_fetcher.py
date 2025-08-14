"""Service for fetching OWASP project levels from GitHub repository."""

import json
import logging
from typing import Dict

import requests
from requests.exceptions import RequestException

from apps.owasp.constants import OWASP_PROJECT_LEVELS_URL

logger = logging.getLogger(__name__)


def fetch_official_project_levels(timeout: int = 30) -> Dict[str, str] | None:
    """Fetch project levels from OWASP GitHub repository.

    Args:
        timeout: HTTP request timeout in seconds

    Returns:
        Dict mapping project names to their official levels, or None if fetch fails

    """
    try:
        response = requests.get(
            OWASP_PROJECT_LEVELS_URL,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            logger.exception(
                "Invalid project levels data format", 
                extra={"expected": "list", "got": type(data).__name__}
            )
            return None

        # Convert the list to a dict mapping project names to their levels
        project_levels = {}
        
        for entry in data:
            if not isinstance(entry, dict):
                continue
            project_name = entry.get("name")
            level = entry.get("level")
            if (
                isinstance(project_name, str)
                and isinstance(level, (str, int, float))
                and project_name.strip()
            ):
                project_levels[project_name.strip()] = str(level)

        return project_levels

    except (RequestException, ValueError) as e:
        logger.exception(
            "Failed to fetch project levels",
            extra={"url": OWASP_PROJECT_LEVELS_URL, "error": str(e)}
        )
        return None

