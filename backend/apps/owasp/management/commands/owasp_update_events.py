"""A command to update OWASP events."""

import yaml
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.github.utils import get_repository_file_content, normalize_url
from apps.owasp.models.event import Event, EventCategory
from apps.owasp.utils import parse_event_dates


class Command(BaseCommand):
    help = "Import events from the provided YAML file"

    def handle(self, *args, **kwargs):
        url = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/events.yml"
        yaml_content = get_repository_file_content(url)
        data = yaml.safe_load(yaml_content)
        events = []

        for category in data:
            category_name = category.get("category", "")
            category_description = category.get("description", "")

            for event_data in category["events"]:
                event_name_slug = slugify(event_data.get("name", ""))
                key = event_name_slug
                end_date = parse_event_dates(
                    event_data.get("dates", ""), event_data.get("start-date")
                )

                fields = {
                    "category": get_event_category(category_name),
                    "category_description": category_description,
                    "end_date": end_date,
                    "key": key,
                    "name": event_data.get("name", ""),
                    "description": event_data.get("optional-text", ""),
                    "start_date": event_data.get("start-date", None),
                    "url": normalize_url(event_data.get("url", "")) or "",
                }

                try:
                    event = Event.objects.get(key=key)
                    # Update existing event
                    for key, value in fields.items():
                        setattr(event, key, value)
                    events.append(event)
                except Event.DoesNotExist:
                    # Create new event
                    event = Event(**fields)
                    events.append(event)

        if events:
            self.stdout.write(f"Saving {len(events)} events...")
            Event.bulk_save(events, fields)
            self.stdout.write(self.style.SUCCESS("Successfully saved events"))
        else:
            self.stdout.write(self.style.WARNING("No events to save"))


def get_event_category(category_name):
    """Get event category."""
    category_map = {
        "Global": EventCategory.GLOBAL,
        "AppSec Days": EventCategory.APPSEC_DAYS,
        "Partner": EventCategory.PARTNER,
    }
    return category_map.get(category_name, EventCategory.OTHER)
