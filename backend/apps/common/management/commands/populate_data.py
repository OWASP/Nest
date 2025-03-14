"""A command to populate all Typesense indexes with database data."""

from django.core.management.base import BaseCommand
from typesense.exceptions import TypsesenseClientError

from apps.common.typesense import REGISTERED_INDEXES


class Command(BaseCommand):
    help = "Populate all Typesense indexes with database data"

    def handle(self, *args, **kwargs):
        for index_name, index_instance in REGISTERED_INDEXES.items():
            self.stdout.write(f"Populating '{index_name}'...")

            try:
                index_instance.populate_collection()
                self.stdout.write(self.style.SUCCESS(f"Successfully populated '{index_name}'"))
            except TypsesenseClientError as e:
                self.stdout.write(self.style.ERROR(f"Failed to populate '{index_name}': {e}"))
