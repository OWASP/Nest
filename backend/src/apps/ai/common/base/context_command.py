"""Base context command class for creating contexts."""

from django.db.models import Model

from apps.ai.common.base.ai_command import BaseAICommand
from apps.ai.models.context import Context


class BaseContextCommand(BaseAICommand):
    """Base class for context creation commands."""

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

            if Context.update_data(
                content=full_content,
                entity=entity,
                source=self.source_name(),
            ):
                processed += 1
                entity_key = self.get_entity_key(entity)
                self.stdout.write(f"Created/updated context for {entity_key}")
            else:
                entity_key = self.get_entity_key(entity)
                self.stdout.write(
                    self.style.ERROR(f"Failed to create/update context for {entity_key}")
                )

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
