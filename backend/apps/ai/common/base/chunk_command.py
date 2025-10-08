"""Base chunk command class for creating chunks."""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Max, Model

from apps.ai.common.base.ai_command import BaseAICommand
from apps.ai.common.utils import create_chunks_and_embeddings
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
from apps.common.utils import is_valid_json


class BaseChunkCommand(BaseAICommand):
    """Base class for chunk creation commands."""

    def help(self) -> str:
        """Return help text for the chunk creation command."""
        return f"Create or update chunks for OWASP {self.entity_name} data"

    def process_chunks_batch(self, entities: list[Model]) -> int:
        """Process a batch of entities to create or update chunks."""
        processed = 0
        batch_chunks_to_create = []
        content_type = ContentType.objects.get_for_model(self.model_class)

        for entity in entities:
            entity_key = self.get_entity_key(entity)
            context = Context.objects.filter(entity_type=content_type, entity_id=entity.id).first()

            if not context:
                self.stdout.write(
                    self.style.WARNING(f"No context found for {self.entity_name} {entity_key}")
                )
                continue

            latest_chunk_timestamp = context.chunks.aggregate(
                latest_created=Max("nest_created_at")
            )["latest_created"]

            if not latest_chunk_timestamp or context.nest_updated_at > latest_chunk_timestamp:
                self.stdout.write(f"Context for {entity_key} requires chunk creation/update")

                if latest_chunk_timestamp:
                    count, _ = context.chunks.all().delete()
                    self.stdout.write(f"Deleted {count} stale chunks for {entity_key}")

                content, metadata_content = self.extract_content(entity)

                if is_valid_json(content):
                    full_content = content
                else:
                    full_content = (
                        f"{metadata_content}\n\n{content}" if metadata_content else content
                    )

                if not full_content.strip():
                    self.stdout.write(f"No content to chunk for {self.entity_name} {entity_key}")
                    continue

                if not (unique_chunk_texts := set(Chunk.split_text(full_content))):
                    self.stdout.write(f"No chunks created for {self.entity_name} {entity_key}")
                    continue

                if chunks := create_chunks_and_embeddings(
                    chunk_texts=list(unique_chunk_texts),
                    context=context,
                    openai_client=self.openai_client,
                    save=False,
                ):
                    batch_chunks_to_create.extend(chunks)
                    processed += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Created {len(chunks)} new chunks for {entity_key}")
                    )
            else:
                self.stdout.write(f"Chunks for {entity_key} are already up to date.")

        if batch_chunks_to_create:
            Chunk.bulk_save(batch_chunks_to_create)

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
