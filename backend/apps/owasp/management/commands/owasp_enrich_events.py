"""A command to enrich events with extra data."""

import logging
import time

from django.core.management.base import BaseCommand

from apps.core.models.prompt import Prompt
from apps.owasp.models.event import Event

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Enrich events with extra data."

    def add_arguments(self, parser):
        parser.add_argument("--offset", default=0, required=False, type=int)

    def handle(self, *args, **options):
        events = Event.objects.order_by("id")
        events_count = events.count()
        all_events = []
        offset = options["offset"]

        for idx, event in enumerate(events[offset:]):
            prefix = f"{idx + offset + 1} of {events_count}"
            print(f"{prefix:<10} {event.url}")
            # Summary.
            if not event.summary and (prompt := Prompt.get_owasp_event_summary()):
                event.generate_summary(prompt=prompt)

            # Suggested location.
            if not event.suggested_location and (
                prompt := Prompt.get_owasp_event_suggested_location()
            ):
                event.generate_suggested_location()

            # Geo location.
            if not event.latitude or not event.longitude:
                try:
                    event.generate_geo_location()
                    time.sleep(5)
                except Exception:
                    logger.exception(
                        "Could not get geo data for event",
                        extra={"url": event.url},
                    )
            all_events.append(event)

        Event.bulk_save(
            all_events,
            fields=("latitude", "longitude", "suggested_location", "summary"),
        )
