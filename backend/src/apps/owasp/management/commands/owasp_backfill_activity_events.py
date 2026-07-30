"""A command to backfill activity events for existing pull requests, issues, and releases."""

import logging

from django.core.management.base import BaseCommand

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

    def backfill_issues(self, offset: int) -> None:
        """Backfill ActivityEvent records for existing issues."""
        issues = Issue.objects.select_related("author", "repository").order_by("created_at")
        issues_count = issues.count()
        self.stdout.write(f"Backfilling activity events for {issues_count} issues...\n")

        created_count = 0
        for issue in issues[offset:]:

            if not issue.repository:
                logger.warning("Skipping issue #%s: no repository", issue.number)
                continue

            try:
                ActivityEvent.update_data(issue)
                created_count += 1
            except Exception:
                logger.exception("Error backfilling activity events for issue #%s", issue.number)

        self.stdout.write(f"Issues processed: {created_count}\n")

    def backfill_pull_requests(self, offset: int) -> None:
        """Backfill ActivityEvent records for existing pull requests."""
        pull_requests = PullRequest.objects.select_related("author", "repository").order_by(
            "created_at"
        )
        pull_requests_count = pull_requests.count()
        self.stdout.write(
            f"Backfilling activity events for {pull_requests_count} pull requests...\n"
        )

        created_count = 0
        for pull_request in pull_requests[offset:]:

            if not pull_request.repository:
                logger.warning(
                    "Skipping pull request #%s: no repository", pull_request.number
                )
                continue

            try:
                ActivityEvent.update_data(pull_request)
                created_count += 1
            except Exception:
                logger.exception(
                    "Error backfilling activity events for pull request #%s",
                    pull_request.number,
                )

        self.stdout.write(f"Pull requests processed: {created_count}\n")

    def backfill_releases(self, offset: int) -> None:
        """Backfill ActivityEvent records for existing releases."""
        releases = Release.objects.select_related("author", "repository").order_by("created_at")
        releases_count = releases.count()
        self.stdout.write(f"Backfilling activity events for {releases_count} releases...\n")

        created_count = 0
        for release in releases[offset:]:

            if not release.repository:
                logger.warning("Skipping release %s: no repository", release.tag_name)
                continue

            try:
                ActivityEvent.update_data(release)
                created_count += 1
            except Exception:
                logger.exception(
                    "Error backfilling activity events for release %s", release.tag_name
                )

        self.stdout.write(f"Releases processed: {created_count}\n")
