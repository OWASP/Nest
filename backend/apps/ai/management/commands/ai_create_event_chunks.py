"""A command to create chunks of OWASP event data for RAG."""

import os
import time
from datetime import UTC, datetime, timedelta

import openai
from django.core.management.base import BaseCommand

from apps.ai.common.constants import (
    DEFAULT_LAST_REQUEST_OFFSET_SECONDS,
    DELIMITER,
    MIN_REQUEST_INTERVAL_SECONDS,
)
from apps.ai.models.chunk import Chunk
from apps.owasp.models.event import Event


class Command(BaseCommand):
    help = "Create chunks for OWASP event data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--event",
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

    def handle(self, *args, **options):
        if not (openai_api_key := os.getenv("DJANGO_OPEN_AI_SECRET_KEY")):
            self.stdout.write(
                self.style.ERROR("DJANGO_OPEN_AI_SECRET_KEY environment variable not set")
            )
            return

        self.openai_client = openai.OpenAI(api_key=openai_api_key)

        if event := options["event"]:
            queryset = Event.objects.filter(key=event)
        elif options["all"]:
            queryset = Event.objects.all()
        else:
            queryset = Event.upcoming_events()

        if not (total_events := queryset.count()):
            self.stdout.write("No events found to process")
            return

        self.stdout.write(f"Found {total_events} events to process")

        batch_size = options["batch_size"]
        for offset in range(0, total_events, batch_size):
            batch_events = queryset[offset : offset + batch_size]

            batch_chunks = []
            for event in batch_events:
                batch_chunks.extend(self.create_chunks(event))

            if batch_chunks:
                Chunk.bulk_save(batch_chunks)
                self.stdout.write(f"Saved {len(batch_chunks)} chunks")

        self.stdout.write(f"Completed processing all {total_events} events")

    def create_chunks(self, event: Event) -> list[Chunk]:
        """Create chunks from an event's data."""
        prose_content, metadata_content = self.extract_event_content(event)

        all_chunk_texts = []

        if metadata_content.strip():
            all_chunk_texts.append(metadata_content)

        if prose_content.strip():
            all_chunk_texts.extend(Chunk.split_text(prose_content))

        if not all_chunk_texts:
            self.stdout.write(f"No content to chunk for event {event.key}")
            return []

        try:
            time_since_last_request = datetime.now(UTC) - getattr(
                self,
                "last_request_time",
                datetime.now(UTC) - timedelta(seconds=DEFAULT_LAST_REQUEST_OFFSET_SECONDS),
            )

            if time_since_last_request < timedelta(seconds=MIN_REQUEST_INTERVAL_SECONDS):
                time.sleep(MIN_REQUEST_INTERVAL_SECONDS - time_since_last_request.total_seconds())

            response = self.openai_client.embeddings.create(
                input=all_chunk_texts,
                model="text-embedding-3-small",
            )
            self.last_request_time = datetime.now(UTC)

            return [
                chunk
                for text, embedding in zip(
                    all_chunk_texts,
                    [d.embedding for d in response.data],
                    strict=True,
                )
                if (
                    chunk := Chunk.update_data(
                        text=text,
                        content_object=event,
                        embedding=embedding,
                        save=False,
                    )
                )
            ]
        except openai.OpenAIError as e:
            self.stdout.write(self.style.ERROR(f"OpenAI API error for event {event.key}: {e}"))
            return []

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