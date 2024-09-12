"""A command to load OWASP Nest data."""

import contextlib

from algoliasearch_django import register, unregister
from algoliasearch_django.registration import RegistrationError
from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Load OWASP Nest data."

    def handle(self, *_args, **_options):
        nest_apps = ("github", "owasp")

        # Disable indexing
        for nest_app in nest_apps:
            for model in apps.get_app_config(nest_app).get_models():
                with contextlib.suppress(RegistrationError):
                    unregister(model)

        # Run loaddata
        with transaction.atomic():
            call_command("loaddata", "data/nest.json", "-v", "3")

        # Enable indexing
        for nest_app in nest_apps:
            for model in apps.get_app_config(nest_app).get_models():
                with contextlib.suppress(RegistrationError):
                    register(model)
