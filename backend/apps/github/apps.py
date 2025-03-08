from importlib import import_module

from django.apps import AppConfig


class GithubConfig(AppConfig):
    name = "apps.github"

    def ready(self):
        import_module("apps.github.schema")
