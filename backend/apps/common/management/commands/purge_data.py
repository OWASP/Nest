"""A command to purge OWASP Nest data."""

# ruff: noqa: SLF001 https://docs.astral.sh/ruff/rules/private-member-access/

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Purge OWASP Nest data."

    def handle(self, *_args, **options) -> None:
        """Purge data from specified OWASP Nest applications."""
        nest_apps = (
            "github",
            "owasp",
            "slack",
        )

        with connection.cursor() as cursor:
            for nest_app in nest_apps:
                for model in sorted(
                    apps.get_app_config(nest_app).get_models(),
                    key=lambda m: m.__name__,
                ):
                    cursor.execute(f"TRUNCATE TABLE {model._meta.db_table} CASCADE")  # NOSONAR
                    print(f"Purged {nest_app}.{model.__name__}")
