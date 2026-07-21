"""A base command that can be inherited to generate metadata."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from django.core.management.base import BaseCommand
from django.db import models
from owasp_schema import get_schema
from owasp_schema.utils.schema_validators import validate_data

logger = logging.getLogger(__name__)


class EntityMetadataBase(BaseCommand, ABC):
    """A base command to generate metadata files."""

    model: models.Model = None

    def add_arguments(self, parser):
        parser.add_argument(
            "entity_key",
            type=str,
            help="The key of the entity to generate the metadata file for.",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        if not self.model:
            self.stderr.write(self.style.ERROR("OWASP entity model is not set."))
            return

        entity_key = options["entity_key"]
        schema_name = self.model.__name__.lower()

        try:
            entity = self.model.objects.get(key=entity_key)
        except self.model.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f"{self.model.__name__} with key '{entity_key}' not found.")
            )
            return

        metadata = self.get_metadata(entity)
        if error_message := validate_data(schema=get_schema(schema_name), data=metadata):
            self.stderr.write(self.style.ERROR("Validation FAILED!"))
            self.stderr.write(f"Reason: {error_message}")
            return

        output_dir = Path(f"data/schema/{schema_name}")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file_path = output_dir / f"{entity_key}.owasp.yaml"
        with output_file_path.open("w") as f:
            yaml.dump(metadata, f, sort_keys=True, default_flow_style=False, indent=4)

        self.stdout.write(self.style.SUCCESS(f"Successfully generated file: {output_file_path}"))

    @abstractmethod
    def get_metadata(self, entity: models.Model) -> dict:
        """Get entity metadata."""
        return {}
