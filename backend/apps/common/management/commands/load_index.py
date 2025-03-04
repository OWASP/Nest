import logging
from django.core.management.base import BaseCommand
import apps.owasp.schema

from apps.common.typesense import REGISTERED_INDEXES


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Command(BaseCommand):
    help = "Create Typesense indexes"

    def handle(self, *args, **kwargs):
        logging.info("Starting Typesense index creation...")
        if not REGISTERED_INDEXES:
            logging.info("No registered indexes found.")
        else:
            logging.info(f"Registered indexes: {list(REGISTERED_INDEXES.values())}")
        for index in REGISTERED_INDEXES.values():
            index.create_collection()

        logging.info("Typesense index creation complete!")
