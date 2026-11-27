"""A command to update OWASP Nest index synonyms."""

from django.core.management.base import BaseCommand

from apps.github.index import IssueIndex
from apps.owasp.index import ProjectIndex


class Command(BaseCommand):
    help = "Update OWASP Nest index synonyms."

    def handle(self, *_args, **_options) -> None:
        """Update synonyms for Algolia indices."""
        self.stdout.write("\nThe following models synonyms were reindexed:")
        for index in (IssueIndex, ProjectIndex):
            count = index.update_synonyms()
            if count:
                self.stdout.write(f"{7 * ' '} * {index.index_name.capitalize()} --> {count}")
