"""A command to update context for OWASP event data."""

from django.core.management.base import BaseCommand

from apps.ai.common.extractors import extract_event_content
from apps.ai.common.utils import create_context
from apps.owasp.models.event import Event


class Command(BaseCommand):
    help = "Update context for OWASP event data"

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

    def handle(self, *args, **options):
        if options["event_key"]:
            queryset = Event.objects.filter(key=options["event_key"])
        elif options["all"]:
            queryset = Event.objects.all()
        else:
            queryset = Event.upcoming_events()
        queryset = queryset.order_by("id")

        if not (total_events := queryset.count()):
            self.stdout.write("No events found to process")
            return

        self.stdout.write(f"Found {total_events} events to process")

        batch_size = options["batch_size"]
        processed_count = 0

        for offset in range(0, total_events, batch_size):
            batch_events = queryset[offset : offset + batch_size]
            processed_count += self.process_context_batch(batch_events)

        self.stdout.write(
            self.style.SUCCESS(f"Completed processing {processed_count}/{total_events} events")
        )

    def process_context_batch(self, events: list[Event]) -> int:
        """Process a batch of events to create contexts."""
        processed = 0

        for event in events:
            prose_content, metadata_content = extract_event_content(event)
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
