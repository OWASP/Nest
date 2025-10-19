"""A command to create member snapshots for a specific user."""

import logging
from collections import defaultdict
from datetime import UTC, datetime

from django.core.management.base import BaseCommand

from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User
from apps.owasp.models.member_snapshot import MemberSnapshot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to create a member snapshot for a specific user."""

    help = "Create a member snapshot for a specific user with their contributions"

    def add_arguments(self, parser):
        """Add command-line arguments.

        Args:
            parser (argparse.ArgumentParser): The argument parser instance.

        """
        parser.add_argument(
            "username",
            type=str,
            help="GitHub username to create snapshot for",
        )
        parser.add_argument(
            "--start-at",
            type=str,
            help="Start date (YYYY-MM-DD). Defaults to January 1st of current year.",
        )
        parser.add_argument(
            "--end-at",
            type=str,
            help="End date (YYYY-MM-DD). Defaults to October 1st of current year.",
        )

    def parse_date(self, date_str: str | None, default: datetime) -> datetime:
        """Parse date string or return default.

        Args:
            date_str (str | None): Date string in YYYY-MM-DD format.
            default (datetime): Default datetime to use if date_str is None.

        Returns:
            datetime: Parsed datetime or default.

        Raises:
            ValueError: If date string format is invalid.

        """
        if not date_str:
            return default

        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
        except ValueError:
            error_msg = f"Invalid date format: {date_str}. Use YYYY-MM-DD."
            self.stderr.write(self.style.ERROR(error_msg))
            raise

    def handle(self, *args, **options):
        """Handle command execution.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments containing command options.

        """
        username = options["username"]

        # Default to current year: Jan 1 to Oct 1
        current_year = datetime.now(UTC).year
        default_start = datetime(current_year, 1, 1, tzinfo=UTC)
        default_end = datetime(current_year, 10, 1, tzinfo=UTC)

        end_at = self.parse_date(options.get("end_at"), default_end)
        start_at = self.parse_date(options.get("start_at"), default_start)

        self.stdout.write(f"Creating snapshot for user: {username}")
        self.stdout.write(f"Period: {start_at.date()} to {end_at.date()}")
        logger.info(
            "Creating snapshot for %s from %s to %s",
            username,
            start_at.date(),
            end_at.date(),
        )

        # Get user
        try:
            user = User.objects.get(login=username)
        except User.DoesNotExist:
            error_msg = f"User '{username}' not found in database"
            self.stderr.write(self.style.ERROR(error_msg))
            logger.exception("User %s not found", username)
            return

        # Check if snapshot already exists
        existing_snapshot = MemberSnapshot.objects.filter(
            github_user=user,
            start_at=start_at,
            end_at=end_at,
        ).first()

        if existing_snapshot:
            self.stdout.write(
                self.style.WARNING(
                    f"Snapshot already exists for this period (ID: {existing_snapshot.id})"
                )
            )
            self.stdout.write("Updating existing snapshot...")
            snapshot = existing_snapshot
            # Clear existing relationships
            snapshot.commits.clear()
            snapshot.pull_requests.clear()
            snapshot.issues.clear()
            logger.info("Updating existing snapshot %s", snapshot.id)
        else:
            # Create new snapshot
            snapshot = MemberSnapshot.objects.create(
                github_user=user,
                start_at=start_at,
                end_at=end_at,
            )
            self.stdout.write(f"Created new snapshot (ID: {snapshot.id})")
            logger.info("Created new snapshot %s", snapshot.id)

        # Fetch and link commits
        commits = Commit.objects.filter(
            author=user,
            created_at__gte=start_at,
            created_at__lte=end_at,
        )
        commits_count = commits.count()
        if commits_count > 0:
            snapshot.commits.add(*commits)
            self.stdout.write(f"  Linked {commits_count} commit(s)")
            logger.info("Linked %s commits to snapshot", commits_count)

        # Fetch and link pull requests
        pull_requests = PullRequest.objects.filter(
            author=user,
            created_at__gte=start_at,
            created_at__lte=end_at,
        )
        prs_count = pull_requests.count()
        if prs_count > 0:
            snapshot.pull_requests.add(*pull_requests)
            self.stdout.write(f"  Linked {prs_count} pull request(s)")
            logger.info("Linked %s pull requests to snapshot", prs_count)

        # Fetch and link issues
        issues = Issue.objects.filter(
            author=user,
            created_at__gte=start_at,
            created_at__lte=end_at,
        )
        issues_count = issues.count()
        if issues_count > 0:
            snapshot.issues.add(*issues)
            self.stdout.write(f"  Linked {issues_count} issue(s)")
            logger.info("Linked %s issues to snapshot", issues_count)

        # Generate heatmap data
        heatmap_data = defaultdict(int)

        for commit in commits:
            date_key = commit.created_at.date().isoformat()
            heatmap_data[date_key] += 1

        for pr in pull_requests:
            date_key = pr.created_at.date().isoformat()
            heatmap_data[date_key] += 1

        for issue in issues:
            date_key = issue.created_at.date().isoformat()
            heatmap_data[date_key] += 1

        snapshot.contribution_heatmap_data = dict(heatmap_data)
        snapshot.save()

        if heatmap_data:
            self.stdout.write(f"  Generated heatmap data for {len(heatmap_data)} day(s)")
            logger.info("Generated heatmap data for %s days", len(heatmap_data))

        # Summary
        total = snapshot.total_contributions
        if total > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSnapshot created successfully for {username}!\n"
                    f"Total contributions: {total} "
                    f"({commits_count} commits, {prs_count} PRs, {issues_count} issues)"
                )
            )
            logger.info(
                "Snapshot completed: %s total contributions for %s",
                total,
                username,
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"\nSnapshot created but no contributions found for {username} "
                    f"in the period {start_at.date()} to {end_at.date()}"
                )
            )
            logger.warning(
                "No contributions found for %s in period %s to %s",
                username,
                start_at.date(),
                end_at.date(),
            )
