from importlib import import_module

from django.apps import AppConfig


class OwaspConfig(AppConfig):
    name = "apps.owasp"

    def ready(self):
        """Import the schema module when the app is ready."""
        import_module("apps.owasp.schema")
