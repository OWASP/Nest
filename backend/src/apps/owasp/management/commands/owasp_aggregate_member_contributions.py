"""Management command to aggregate user contribution data."""

from datetime import datetime, timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Count, Exists, OuterRef, Q
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.user import User


class Command(BaseCommand):
    """Aggregate contribution data for users."""

    help = "Aggregate contribution data (commits, PRs, issues) for users"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--user",
            type=str,
            help="Specific user login to process",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=365,
            help="Number of days to look back (default: 365)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Batch size for processing users (default: 100)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution."""
        user_login = options.get("user")
        days = options.get("days", 365)
        batch_size = options.get("batch_size", 100)

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        self.stdout.write(
            self.style.SUCCESS(
                f"Aggregating contributions since {start_date.date()} ({days} days back)"
            )
        )

        if user_login:
            users = User.objects.filter(login=user_login)
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"Member '{user_login}' not found"))
                return
        else:
            users = User.objects.alias(
                has_commits=Exists(
                    Commit.objects.filter(
                        author_id=OuterRef("pk"),
                        created_at__gte=start_date,
                        created_at__lte=end_date,
                    )
                ),
                has_issues=Exists(
                    Issue.objects.filter(
                        author_id=OuterRef("pk"),
                        created_at__gte=start_date,
                        created_at__lte=end_date,
                    )
                ),
                has_pull_requests=Exists(
                    PullRequest.objects.filter(
                        author_id=OuterRef("pk"),
                        created_at__gte=start_date,
                        created_at__lte=end_date,
                    )
                ),
            ).filter(
                Q(contributions_count__gt=0)
                | Q(has_commits=True)
                | Q(has_issues=True)
                | Q(has_pull_requests=True)
                | (Q(contribution_data__isnull=False) & ~Q(contribution_data={}))
            )

        total_users = users.count()
        self.stdout.write(f"Processing {total_users} members...")

        updated_users = []
        for user in users.iterator(chunk_size=batch_size):
            user.contribution_data = self._aggregate_user_contributions(user, start_date, end_date)
            updated_users.append(user)

        User.bulk_save(updated_users, fields=["contribution_data"])

        self.stdout.write(
            self.style.SUCCESS(f"Successfully aggregated contributions for {total_users} members")
        )

    def _aggregate_user_contributions(
        self, user: User, start_date: datetime, end_date: datetime | None = None
    ) -> dict[str, int]:
        """Aggregate contributions for a user.

        Args:
            user: User instance
            start_date: Start datetime for aggregation
            end_date: Inclusive end datetime for aggregation; defaults to now

        Returns:
            Dictionary mapping YYYY-MM-DD to contribution counts

        """
        contribution_data = {}
        current_date = start_date.date()
        end_date = end_date or timezone.now()

        while current_date <= end_date.date():
            date_str = current_date.strftime("%Y-%m-%d")
            contribution_data[date_str] = 0
            current_date += timedelta(days=1)

        commits = (
            Commit.objects.filter(
                author=user,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
        )

        for commit in commits:
            date_str = commit["date"].strftime("%Y-%m-%d")
            contribution_data[date_str] = contribution_data.get(date_str, 0) + commit["count"]

        prs = (
            PullRequest.objects.filter(
                author=user,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
        )

        for pr in prs:
            date_str = pr["date"].strftime("%Y-%m-%d")
            contribution_data[date_str] = contribution_data.get(date_str, 0) + pr["count"]

        issues = (
            Issue.objects.filter(
                author=user,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
        )

        for issue in issues:
            date_str = issue["date"].strftime("%Y-%m-%d")
            contribution_data[date_str] = contribution_data.get(date_str, 0) + issue["count"]

        return contribution_data
