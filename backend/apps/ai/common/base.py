"""Base classes for AI management commands."""

import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Model, QuerySet

from apps.ai.common.utils import create_chunks_and_embeddings, create_context
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context


class BaseAICommand(BaseCommand, ABC):
    """Base class for AI management commands with common functionality."""

    def __init__(self, *args, **kwargs):
        """Initialize the AI command with OpenAI client placeholder."""
        super().__init__(*args, **kwargs)
        self.openai_client: openai.OpenAI | None = None

    @property
    @abstractmethod
    def model_class(self) -> type[Model]:
        """Return the Django model class this command operates on."""

    @property
    @abstractmethod
    def entity_name(self) -> str:
        """Return the human-readable name for the entity (e.g., 'chapter', 'project')."""

    @property
    @abstractmethod
    def entity_name_plural(self) -> str:
        """Return the plural form of the entity name."""

    @property
    @abstractmethod
    def key_field_name(self) -> str:
        """Return the field name used for filtering by key (e.g., 'key', 'slug')."""

    @abstractmethod
    def extract_content(self, entity: Model) -> tuple[str, str]:
        """Extract content from the entity. Return (prose_content, metadata_content)."""

    @property
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


class BaseContextCommand(BaseAICommand):
    """Base class for context creation commands."""

    @property
    def help(self) -> str:
        """Return help text for the context creation command."""
        return f"Update context for OWASP {self.entity_name} data"

    def process_context_batch(self, entities: list[Model]) -> int:
        """Process a batch of entities to create contexts."""
        processed = 0

        for entity in entities:
            prose_content, metadata_content = self.extract_content(entity)
            full_content = (
                f"{metadata_content}\n\n{prose_content}" if metadata_content else prose_content
            )

            if not full_content.strip():
                entity_key = self.get_entity_key(entity)
                self.stdout.write(f"No content for {self.entity_name} {entity_key}")
                continue

            if create_context(
                content=full_content,
                content_object=entity,
                source=self.source_name,
            ):
                processed += 1
                entity_key = self.get_entity_key(entity)
                self.stdout.write(f"Created context for {entity_key}")
            else:
                entity_key = self.get_entity_key(entity)
                self.stdout.write(self.style.ERROR(f"Failed to create context for {entity_key}"))

        return processed

    def handle(self, *args, **options):
        """Handle the context creation command."""
        queryset = self.get_queryset(options)
        batch_size = options["batch_size"]

        self.handle_batch_processing(
            queryset=queryset,
            batch_size=batch_size,
            process_batch_func=self.process_context_batch,
        )


class BaseChunkCommand(BaseAICommand):
    """Base class for chunk creation commands."""

    @property
    def help(self) -> str:
        """Return help text for the chunk creation command."""
        return f"Create chunks for OWASP {self.entity_name} data"

    def process_chunks_batch(self, entities: list[Model]) -> int:
        """Process a batch of entities to create chunks."""
        processed = 0
        batch_chunks = []
        content_type = ContentType.objects.get_for_model(self.model_class)

        for entity in entities:
            context = Context.objects.filter(
                content_type=content_type, object_id=entity.id
            ).first()

            entity_key = self.get_entity_key(entity)

            if not context:
                self.stdout.write(
                    self.style.WARNING(f"No context found for {self.entity_name} {entity_key}")
                )
                continue

            prose_content, metadata_content = self.extract_content(entity)
            full_content = (
                f"{metadata_content}\n\n{prose_content}" if metadata_content else prose_content
            )

            if not full_content.strip():
                self.stdout.write(f"No content to chunk for {self.entity_name} {entity_key}")
                continue

            chunk_texts = Chunk.split_text(full_content)
            if not chunk_texts:
                self.stdout.write(
                    f"No chunks created for {self.entity_name} {entity_key}: `{full_content}`"
                )
                continue

            if chunks := create_chunks_and_embeddings(
                chunk_texts=chunk_texts,
                context=context,
                openai_client=self.openai_client,
                save=False,
            ):
                batch_chunks.extend(chunks)
                processed += 1
                self.stdout.write(f"Created {len(chunks)} chunks for {entity_key}")

        if batch_chunks:
            Chunk.bulk_save(batch_chunks)

        return processed

    def handle(self, *args, **options):
        """Handle the chunk creation command."""
        if not self.setup_openai_client():
            return

        queryset = self.get_queryset(options)
        batch_size = options["batch_size"]

        self.handle_batch_processing(
            queryset=queryset,
            batch_size=batch_size,
            process_batch_func=self.process_chunks_batch,
        )
