"""A command to purge OWASP Nest data."""

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from psycopg2 import sql


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
                    # Suppress false positive sqlalchemy warning.
                    cursor.execute(  # NOSEMGREP: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query  # noqa: E501
                        sql.SQL("TRUNCATE TABLE {} CASCADE").format(
                            sql.Identifier(model._meta.db_table)
                        )
                    )
                    print(f"Purged {nest_app}.{model.__name__}")
