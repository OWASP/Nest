"""A command to create chunks of OWASP event data for RAG."""

import os

import openai
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.ai.common.constants import DELIMITER
from apps.ai.common.utils import create_chunks_and_embeddings, create_context
from apps.ai.models.chunk import Chunk
from apps.ai.models.context import Context
from apps.owasp.models.event import Event


class Command(BaseCommand):
    help = "Create chunks for OWASP event data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-key",
            type=str,
            help="Process only the event with this key",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all the events",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=50,
            help="Number of events to process in each batch",
        )
        parser.add_argument(
            "--context",
            action="store_true",
            help="Create only context (skip chunks and embeddings)",
        )
        parser.add_argument(
            "--chunks",
            action="store_true",
            help="Create only chunks+embeddings (requires existing context)",
        )

    def handle(self, *args, **options):
        if not options["context"] and not options["chunks"]:
            self.stdout.write(
                self.style.ERROR("Please specify either --context or --chunks (or both)")
            )
            return

        if options["chunks"] and not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        if options["chunks"]:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)

        if options["event_key"]:
            queryset = Event.objects.filter(key=options["event_key"])
        elif options["all"]:
            queryset = Event.objects.all()
        else:
            queryset = Event.upcoming_events()

        if not (total_events := queryset.count()):
            self.stdout.write("No events found to process")
            return

        self.stdout.write(f"Found {total_events} events to process")

        batch_size = options["batch_size"]
        processed_count = 0

        for offset in range(0, total_events, batch_size):
            batch_events = queryset[offset : offset + batch_size]

            if options["context"]:
                processed_count += self.process_context_batch(batch_events)
            elif options["chunks"]:
                processed_count += self.process_chunks_batch(batch_events)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_events} events")
        )

    def process_context_batch(self, events: list[Event]) -> int:
        """Process a batch of events to create contexts."""
        processed = 0

        for event in events:
            prose_content, metadata_content = self.extract_event_content(event)
            full_content = (
                f"{metadata_content}\n\n{prose_content}" if metadata_content else prose_content
            )

            if not full_content.strip():
                self.stdout.write(f"No content for event {event.key}")
                continue

            if create_context(content=full_content, content_object=event, source="owasp_event"):
                processed += 1
                self.stdout.write(f"Created context for {event.key}")
            else:
                self.stdout.write(self.style.ERROR(f"Failed to create context for {event.key}"))
        return processed

    def process_chunks_batch(self, events: list[Event]) -> int:
        """Process a batch of events to create chunks."""
        processed = 0
        batch_chunks = []

        event_content_type = ContentType.objects.get_for_model(Event)

        for event in events:
            context = Context.objects.filter(
                content_type=event_content_type, object_id=event.id
            ).first()

            if not context:
                self.stdout.write(self.style.WARNING(f"No context found for event {event.key}"))
                continue

            prose_content, metadata_content = self.extract_event_content(event)
            all_chunk_texts = []

            if metadata_content.strip():
                all_chunk_texts.append(metadata_content)

            if prose_content.strip():
                prose_chunks = Chunk.split_text(prose_content)
                all_chunk_texts.extend(prose_chunks)

            if not all_chunk_texts:
                self.stdout.write(f"No content to chunk for event {event.key}")
                continue

            if chunks := create_chunks_and_embeddings(
                chunk_texts=all_chunk_texts,
                context=context,
                openai_client=self.openai_client,
                save=False,
            ):
                batch_chunks.extend(chunks)
                processed += 1
                self.stdout.write(f"Created {len(chunks)} chunks for {event.key}")

        if batch_chunks:
            Chunk.bulk_save(batch_chunks)
        return processed

    def extract_event_content(self, event: Event) -> tuple[str, str]:
        """Extract and separate prose content from metadata for an event.

        Returns:
          tuple[str, str]: (prose_content, metadata_content)

        """
        prose_parts = []
        metadata_parts = []

        if event.description:
            prose_parts.append(f"Description: {event.description}")

        if event.summary:
            prose_parts.append(f"Summary: {event.summary}")

        if event.name:
            metadata_parts.append(f"Event Name: {event.name}")

        if event.category:
            metadata_parts.append(f"Category: {event.get_category_display()}")

        if event.start_date:
            metadata_parts.append(f"Start Date: {event.start_date}")

        if event.end_date:
            metadata_parts.append(f"End Date: {event.end_date}")

        if event.suggested_location:
            metadata_parts.append(f"Location: {event.suggested_location}")

        if event.latitude and event.longitude:
            metadata_parts.append(f"Coordinates: {event.latitude}, {event.longitude}")

        if event.url:
            metadata_parts.append(f"Event URL: {event.url}")

        return (
            DELIMITER.join(filter(None, prose_parts)),
            DELIMITER.join(filter(None, metadata_parts)),
        )
