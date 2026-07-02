"""Base AI command class with common functionality."""

import os
from collections.abc import Callable
from typing import Any

import openai
from django.core.management.base import BaseCommand
from django.db.models import Model, QuerySet


class BaseAICommand(BaseCommand):
    """Base class for AI management commands with common functionality."""

    model_class: type[Model]
    key_field_name: str

    def __init__(self, *args, **kwargs):
        """Initialize the AI command with OpenAI client placeholder."""
        super().__init__(*args, **kwargs)
        self.entity_name = self.model_class.__name__.lower()
        self.entity_name_plural = self.model_class.__name__.lower() + "s"
        self.openai_client = None

    def source_name(self) -> str:
        """Return the source name for context creation. Override if different from default."""
        return f"owasp_{self.entity_name}"

    def get_base_queryset(self) -> QuerySet:
        """Return the base queryset. Override for custom filtering logic."""
        return self.model_class.objects.all()

    def get_default_queryset(self) -> QuerySet:
        """Return the default queryset when no specific options are provided."""
        return self.get_base_queryset().filter(is_active=True)

    def add_common_arguments(self, parser):
        """Add common arguments that most commands need."""
        parser.add_argument(
            f"--{self.entity_name}-key",
            type=str,
            help=f"Process only the {self.entity_name} with this key",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help=f"Process all the {self.entity_name_plural}",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help=f"Number of {self.entity_name_plural} to process in each batch",
        )

    def add_arguments(self, parser):
        """Add arguments to the command. Override to add custom arguments."""
        self.add_common_arguments(parser)

    def get_queryset(self, options: dict[str, Any]) -> QuerySet:
        """Get the queryset based on command options."""
        key_option = f"{self.entity_name}_key"

        if options.get(key_option):
            filter_kwargs = {self.key_field_name: options[key_option]}
            return self.get_base_queryset().filter(**filter_kwargs)
        if options.get("all"):
            return self.get_base_queryset()
        return self.get_default_queryset()

    def get_entity_key(self, entity: Model) -> str:
        """Get the key/identifier for an entity for display purposes."""
        return str(getattr(entity, self.key_field_name, entity.pk))

    def setup_openai_client(self) -> bool:
        """Set up OpenAI client if API key is available."""
        if openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY"):
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
            return True
        self.stdout.write(
            self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
        )
        return False

    def handle_batch_processing(
        self,
        queryset: QuerySet,
        batch_size: int,
        process_batch_func: Callable[[list[Model]], int],
    ) -> None:
        """Handle the common batch processing logic."""
        total_count = queryset.count()

        if not total_count:
            self.stdout.write(f"No {self.entity_name_plural} found to process")
            return

        self.stdout.write(f"Found {total_count} {self.entity_name_plural} to process")

        processed_count = 0
        for offset in range(0, total_count, batch_size):
            batch_items = queryset[offset : offset + batch_size]
            processed_count += process_batch_func(list(batch_items))

        self.stdout.write(
            self.style.SUCCESS(
                f"Completed processing {processed_count}/{total_count} {self.entity_name_plural}"
            )
        )
