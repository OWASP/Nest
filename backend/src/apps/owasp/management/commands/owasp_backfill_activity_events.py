"""A command to backfill activity events for existing pull requests, issues, and releases."""

import logging
from collections.abc import Callable
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import QuerySet

from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.owasp.models.activity_event import ActivityEvent

logger: logging.Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfill ActivityEvent records for existing pull requests, issues, and releases."

    def add_arguments(self, parser) -> None:
        """Add command-line arguments to the parser."""
        parser.add_argument(
            "--offset",
            default=0,
            required=False,
            type=int,
            help="Number of records to skip before starting backfill.",
        )
        parser.add_argument(
            "--model",
            default="all",
            required=False,
            choices=["all", "issue", "pull_request", "release"],
            help="Which model type to backfill. Defaults to 'all'.",
        )

    def handle(self, *args, **options) -> None:
        """Handle the command execution."""
        offset = options["offset"]
        model = options["model"]

        if model in ("all", "issue"):
            self.backfill_issues(offset)

        if model in ("all", "pull_request"):
            self.backfill_pull_requests(offset)

        if model in ("all", "release"):
            self.backfill_releases(offset)

    def backfill_objects(
        self,
        queryset: QuerySet,
        offset: int,
        noun: str,
        get_label: Callable[[Any], str],
    ) -> None:
        """Backfill ActivityEvent records for a queryset of GitHub objects."""
        count = queryset.count()
        self.stdout.write(f"Backfilling activity events for {count} {noun}...\n")

        created_count = 0
        for obj in queryset[offset:].iterator(chunk_size=2000):
            if not obj.repository:
                logger.warning("Skipping %s %s: no repository", noun.rstrip("s"), get_label(obj))
                continue

            try:
                ActivityEvent.update_data(obj)
                created_count += 1
            except Exception:
                logger.exception(
                    "Error backfilling activity events for %s %s",
                    noun.rstrip("s"),
                    get_label(obj),
                )

        self.stdout.write(f"{noun.capitalize()} processed: {created_count}\n")

    def backfill_issues(self, offset: int) -> None:
        """Backfill ActivityEvent records for existing issues."""
        queryset = Issue.objects.select_related("author", "repository").order_by(
            "created_at", "pk"
        )
        self.backfill_objects(queryset, offset, "issues", lambda obj: f"#{obj.number}")

    def backfill_pull_requests(self, offset: int) -> None:
        """Backfill ActivityEvent records for existing pull requests."""
        queryset = PullRequest.objects.select_related("author", "repository").order_by(
            "created_at", "pk"
        )
        self.backfill_objects(queryset, offset, "pull requests", lambda obj: f"#{obj.number}")

    def backfill_releases(self, offset: int) -> None:
        """Backfill ActivityEvent records for existing releases."""
        queryset = Release.objects.select_related("author", "repository").order_by(
            "created_at", "pk"
        )
        self.backfill_objects(queryset, offset, "releases", lambda obj: obj.tag_name)
