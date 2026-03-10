"""Validators for Algolia search configuration."""
import os
from typing import Dict

from django.core.exceptions import ImproperlyConfigured


class AlgoliaConfigError(ImproperlyConfigured):
    """Exception raised when Algolia is not properly configured."""

    def __init__(self):
        super().__init__(
            "Algolia is not configured. Please check your environment variables: "
            "DJANGO_ALGOLIA_APPLICATION_ID and DJANGO_ALGOLIA_WRITE_API_KEY. "
            "See CONTRIBUTING.md for setup instructions."
        )


def validate_algolia_config() -> Dict[str, str]:
    """
    Validate and return Algolia configuration.
    
    Raises:
        AlgoliaConfigError: If required environment variables are missing.
    
    Returns:
        Dictionary with app_id and api_key if valid.
    """
    app_id = os.getenv("DJANGO_ALGOLIA_APPLICATION_ID", "").strip()
    api_key = os.getenv("DJANGO_ALGOLIA_WRITE_API_KEY", "").strip()

    if not app_id or not api_key:
        raise AlgoliaConfigError()

    return {"app_id": app_id, "api_key": api_key}


def is_algolia_configured() -> bool:
    """Check if Algolia is properly configured."""
    try:
        validate_algolia_config()
        return True
    except AlgoliaConfigError:
        return False
