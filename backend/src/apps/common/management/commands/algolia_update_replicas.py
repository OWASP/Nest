"""A command to update OWASP Nest index replicas."""

import logging

from django.core.management.base import BaseCommand, CommandError

from apps.mentorship.index import ProgramIndex
from apps.owasp.index import ChapterIndex, ProjectIndex

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update OWASP Nest index replicas."

    def handle(self, *_args, **_options) -> None:
        """Update replicas for Algolia indices."""
        self.stdout.write("\n Starting replica configuration...\n")
        failures = []

        for index in (ChapterIndex, ProgramIndex, ProjectIndex):
            try:
                index.configure_replicas()
            except Exception:
                logger.exception("Failed to configure replicas for %s", index.__name__)
                failures.append(index.__name__)

        if failures:
            message = f"Failed to configure replicas for: {', '.join(failures)}"
            raise CommandError(message)

        self.stdout.write(self.style.SUCCESS("\n Replicas have been successfully created.\n"))
