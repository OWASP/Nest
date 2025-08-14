"""OWASP utilities."""

from .compliance_detector import detect_and_update_compliance
from .project_level_fetcher import fetch_official_project_levels

__all__ = ["detect_and_update_compliance", "fetch_official_project_levels"]