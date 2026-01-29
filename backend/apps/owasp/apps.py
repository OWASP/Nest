"""Owasp app config."""

from django.apps import AppConfig


class OwaspConfig(AppConfig):
    """Owasp app config."""

    name = "apps.owasp"

    def ready(self):
        import apps.owasp.signals.snapshot  # noqa: F401
