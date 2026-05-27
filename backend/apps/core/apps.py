"""Core app config."""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    """Core app config."""

    name = "apps.core"

    def ready(self):
        """Validate Algolia configuration on startup."""
        self._validate_algolia_config()

    def _validate_algolia_config(self):
        """Log warning if Algolia credentials are missing."""
        from django.conf import settings

        invalid_values = {"", "none", "null"}

        app_id = str(
            getattr(settings, "ALGOLIA_APPLICATION_ID", "")
        ).strip().lower()

        api_key = str(
            getattr(settings, "ALGOLIA_WRITE_API_KEY", "")
        ).strip().lower()

        if app_id in invalid_values or api_key in invalid_values:
            logger.warning(
                "Algolia is not configured. "
                "Please set ALGOLIA_APPLICATION_ID and "
                "ALGOLIA_WRITE_API_KEY in environment variables."
            )