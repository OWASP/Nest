"""A command to update OWASP Nest index synonyms."""

from django.core.management.base import BaseCommand

from apps.github.index.issue import IssueIndex
from apps.owasp.index.project import ProjectIndex


class Command(BaseCommand):
    help = "Update OWASP Nest index synonyms."

    def handle(self, *_args, **_options):
        """Update synonyms for Algolia indices.

        Args:
        ----
            *_args: Positional arguments (not used).
            **_options: Keyword arguments (not used).

        """
        print("\nThe following models synonyms were reindexed:")
        for index in (IssueIndex, ProjectIndex):
            count = index.update_synonyms()
            if count:
                print(f"{7*' '} * {index.index_name.capitalize()} --> {count}")
