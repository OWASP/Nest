"""A command to purge OWASP Nest data."""

#!/usr/bin/env python3
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Purge OWASP Nest data."

    def handle(self, *_args, **options):
        nest_apps = ("github", "owasp")

        with connection.cursor() as cursor:
            for nest_app in nest_apps:
                for model in apps.get_app_config(nest_app).get_models():
                    cursor.execute(f"TRUNCATE TABLE {model._meta.db_table} CASCADE")
                    print(f"Purged GitHub {model._meta.verbose_name_plural}")
