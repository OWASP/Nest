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


class BaseGenerateMetadataCommand(BaseCommand, ABC):
    """A base command to generate and validate metadata YAML files."""

    model: models.Model = None
    schema_name: str = ""

    def add_arguments(self, parser):
        parser.add_argument(
            "entity_key",
            type=str,
            help="The key of the entity to generate the metadata file for.",
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        if not all([self.model, self.schema_name]):
            self.stderr.write(self.style.ERROR("Fields 'model', 'schema_name' must be set."))
            return

        entity_key = options["entity_key"]

        try:
            entity = self.model.objects.get(key=entity_key)
        except self.model.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f"{self.model.__name__} with key '{entity_key}' not found.")
            )
            return

        metadata_dict = self.map_data_to_schema(entity)

        schema = get_schema(self.schema_name)
        error_message = validate_data(schema=schema, data=metadata_dict)

        if error_message:
            self.stderr.write(self.style.ERROR("Validation FAILED!"))
            self.stderr.write(f"Reason: {error_message}")
            return
        self.stdout.write(self.style.SUCCESS("Validation successful!"))

        output_dir = Path(f"data/schema/{self.schema_name}")
        output_file_path = output_dir / f"{self.schema_name}.owasp.yaml"
        output_dir.mkdir(parents=True, exist_ok=True)

        with output_file_path.open("w") as f:
            yaml.dump(metadata_dict, f, sort_keys=True, default_flow_style=False, indent=4)

        self.stdout.write(self.style.SUCCESS(f"Successfully generated file: {output_file_path}"))

    @abstractmethod
    def map_data_to_schema(self, entity: models.Model) -> dict:
        """Map the entity data to a dictionary that matches the schema."""
