"""Owasp app config."""

from django.apps import AppConfig


class OwaspConfig(AppConfig):
    """Owasp app config."""

    name = "apps.owasp"

    def ready(self):
        """Ready."""
        import apps.owasp.signals  # noqa: F401, PLC0415
