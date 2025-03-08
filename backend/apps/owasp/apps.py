from importlib import import_module

from django.apps import AppConfig


class OwaspConfig(AppConfig):
    name = "apps.owasp"

    def ready(self):
        import_module("apps.owasp.schema")
