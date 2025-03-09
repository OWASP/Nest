"""A command to load OWASP NEST Index."""

import logging

from django.core.management.base import BaseCommand

from apps.common.typesense import REGISTERED_INDEXES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Command(BaseCommand):
    help = "Create Typesense indexes"

    def handle(self, *args, **kwargs):
        logging.info("Starting Typesense index creation...")
        if not REGISTERED_INDEXES:
            logging.info("No registered indexes found.")
        else:
            logging.info("Registered indexes: %s", list(REGISTERED_INDEXES.keys()))
        for index in REGISTERED_INDEXES.values():
            index.create_collection()
            try:
                index.create_collection()
            except Exception:
                logging.exception(
                    "Failed to create collection for index: %s", index.__class__.__name__
                )

        logging.info("Typesense index creation complete!")
