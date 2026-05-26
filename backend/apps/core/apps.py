"""Core app config."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core app config."""

    name = "apps.core"

    def ready(self):
        """Validate Algolia configuration on startup."""
        self._validate_algolia_config()

    def _validate_algolia_config(self):
        """Raise RuntimeError if Algolia credentials are missing or invalid."""
        from django.conf import settings

        invalid_values = {"", "none", "null"}

        app_id = str(getattr(settings, "ALGOLIA_APPLICATION_ID", "")).strip().lower()
        api_key = str(getattr(settings, "ALGOLIA_WRITE_API_KEY", "")).strip().lower()

        if app_id in invalid_values or api_key in invalid_values:
            raise RuntimeError(
                "Algolia is not configured. "
                "Please set ALGOLIA_APPLICATION_ID and "
                "ALGOLIA_WRITE_API_KEY in your environment variables."
                
            )