"""A command to add events data."""

import yaml
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.github.utils import get_repository_file_content, normalize_url
from apps.owasp.models.event import Event


class Command(BaseCommand):
    help = "Import events from the provided YAML file"

    def handle(self, *args, **kwargs):
        url = "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/events.yml"
        yaml_content = get_repository_file_content(url)
        data = yaml.safe_load(yaml_content)

        for category in data:
            category_name = category.get("category", "")
            category_description = category.get("description", "")

            for event_data in category["events"]:
                event_name_slug = slugify(event_data.get("name", ""))
                key = f"www-event-{event_name_slug}"

                fields = {
                    "key": key,
                    "name": event_data.get("name", ""),
                    "url": normalize_url(event_data.get("url", "")) or "",
                    "category": category_name,
                    "dates": event_data.get("dates", ""),
                    "start_date": event_data.get("start-date", None),
                    "optional_text": event_data.get("optional-text", ""),
                    "category_description": category_description,
                }

                try:
                    event = Event.objects.get(name=fields["name"])
                    # Update existing event
                    for key, value in fields.items():
                        setattr(event, key, value)
                    event.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully updated event: {event.name}")
                    )
                except Event.DoesNotExist:
                    # Create new event
                    event = Event(**fields)
                    event.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully created event: {event.name}")
                    )

        self.stdout.write(self.style.SUCCESS("Finished importing events"))
