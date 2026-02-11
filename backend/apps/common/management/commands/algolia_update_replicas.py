"""A command to update OWASP Nest index replicas."""

from django.core.management.base import BaseCommand

from apps.owasp.index import ProjectIndex


class Command(BaseCommand):
    help = "Update OWASP Nest index replicas."

    def handle(self, *_args, **_options) -> None:
        """Update replicas for Algolia indices."""
        self.stdout.write("\n Starting replica configuration...")
        ProjectIndex.configure_replicas()
        self.stdout.write("\n Replica have been Successfully created.")
