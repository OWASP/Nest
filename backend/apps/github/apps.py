from importlib import import_module

from django.apps import AppConfig


class GithubConfig(AppConfig):
    name = "apps.github"

    def ready(self):
        """Import the schema module when the app is ready."""
        import_module("apps.github.schema")
