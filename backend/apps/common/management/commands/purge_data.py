"""A command to purge OWASP Nest data."""

from django.core.management.base import BaseCommand
from django.db import connection

from apps.github.models import Issue, Label, Organization, Release, Repository, User
from apps.owasp.models import Chapter, Committee, Event, Project

BATCH_SIZE = 10


class Command(BaseCommand):
    help = "Purge OWASP Nest data."

    def handle(self, *_args, **options):
        with connection.cursor() as cursor:
            models = (
                Chapter,
                Committee,
                Event,
                Issue,
                Label,
                Organization,
                Project,
                Release,
                Repository,
                User,
            )

            for model in models:
                cursor.execute(f"TRUNCATE TABLE {model._meta.db_table} CASCADE")  # noqa: SLF001
                print(f"Purged GitHub {model._meta.verbose_name_plural}")  # noqa: SLF001
