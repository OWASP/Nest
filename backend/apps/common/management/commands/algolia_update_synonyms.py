"""A command to update OWASP Nest index synonyms."""

from django.core.management.base import BaseCommand

from apps.github.index.issue import IssueIndex
from apps.owasp.index.project import ProjectIndex


class Command(BaseCommand):
    help = "Update OWASP Nest index synonyms."

    def handle(self, *_args, **_options):
        for index in (IssueIndex, ProjectIndex):
            index.update_synonyms()
            print(f"Updated {index.index_name.capitalize()} synonyms")
