"""A command to update OWASP events."""

import yaml
from django.core.management.base import BaseCommand

from apps.github.utils import get_repository_file_content
from apps.owasp.models.event import Event


class Command(BaseCommand):
    help = "Import events from the provided YAML file"

    def handle(self, *args, **kwargs) -> None:
        """Handle the command execution."""
        data = yaml.safe_load(
            get_repository_file_content(
                "https://raw.githubusercontent.com/OWASP/owasp.github.io/main/_data/events.yml"
            )
        )

        Event.bulk_save(
            [
                event
                for category in data
                for event_data in category["events"]
                if (event := Event.update_data(category["category"], event_data, save=False))
            ]
        )
