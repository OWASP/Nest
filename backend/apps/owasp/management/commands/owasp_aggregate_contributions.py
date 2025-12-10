"""Management command to aggregate contributions for chapters and projects."""

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.github.models.commit import Commit
from apps.github.models.issue import Issue
from apps.github.models.pull_request import PullRequest
from apps.github.models.release import Release
from apps.owasp.models.chapter import Chapter
from apps.owasp.models.project import Project


class Command(BaseCommand):
    """Aggregate contribution data for chapters and projects."""

    help = "Aggregate contributions (commits, issues, PRs, releases) for chapters and projects"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--entity-type",
            choices=["chapter", "project"],
            help="Entity type to aggregate: chapter, project",
            required=True,
            type=str,
        )
        parser.add_argument(
            "--days",
            default=365,
            help="Number of days to look back for contributions (default: 365)",
            type=int,
        )
        parser.add_argument(
            "--key",
            help="Specific chapter or project key to aggregate",
            type=str,
        )
        parser.add_argument(
            "--offset",
            default=0,
            help="Skip the first N entities",
            type=int,
        )

    def _aggregate_contribution_dates(
        self,
        queryset,
        date_field: str,
        contribution_map: dict[str, int],
    ) -> None:
        """Aggregate contribution dates from a queryset into the contribution map.

        Args:
            queryset: Django queryset to aggregate
            date_field: Name of the date field to aggregate on
            contribution_map: Dictionary to update with counts

        """
        for date_value in queryset.values_list(date_field, flat=True):
            if not date_value:
                continue

            date_key = date_value.date().isoformat()
            contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

    def aggregate_chapter_contributions(
        self,
        chapter: Chapter,
        start_date: datetime,
    ) -> dict[str, int]:
        """Aggregate contributions for a chapter.

        Args:
            chapter: Chapter instance
            start_date: Start date for aggregation

        Returns:
            Dictionary mapping YYYY-MM-DD to contribution count

        """
        contribution_map: dict[str, int] = {}

        if not chapter.owasp_repository:
            return contribution_map

        repository = chapter.owasp_repository

        # Aggregate commits.
        self._aggregate_contribution_dates(
            Commit.objects.filter(
                repository=repository,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate issues.
        self._aggregate_contribution_dates(
            Issue.objects.filter(
                created_at__gte=start_date,
                repository=repository,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate pull requests.
        self._aggregate_contribution_dates(
            PullRequest.objects.filter(
                created_at__gte=start_date,
                repository=repository,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate published releases.
        self._aggregate_contribution_dates(
            Release.objects.filter(
                is_draft=False,
                published_at__gte=start_date,
                repository=repository,
            ),
            "published_at",
            contribution_map,
        )

        return contribution_map

    def aggregate_project_contributions(
        self,
        project: Project,
        start_date: datetime,
    ) -> dict[str, int]:
        """Aggregate contributions for a project across all its repositories.

        Args:
            project: Project instance
            start_date: Start date for aggregation

        Returns:
            Dictionary mapping YYYY-MM-DD to contribution count

        """
        contribution_map: dict[str, int] = {}

        repository_ids = [r.id for r in project.repositories.all()]
        if project.owasp_repository:
            repository_ids.append(project.owasp_repository.id)

        if not repository_ids:
            return contribution_map

        # Aggregate commits.
        self._aggregate_contribution_dates(
            Commit.objects.filter(
                created_at__gte=start_date,
                repository_id__in=repository_ids,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate issues.
        self._aggregate_contribution_dates(
            Issue.objects.filter(
                repository_id__in=repository_ids,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate pull requests.
        self._aggregate_contribution_dates(
            PullRequest.objects.filter(
                repository_id__in=repository_ids,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate published releases.
        self._aggregate_contribution_dates(
            Release.objects.filter(
                repository_id__in=repository_ids,
                published_at__gte=start_date,
                is_draft=False,
            ),
            "published_at",
            contribution_map,
        )

        return contribution_map

    def calculate_chapter_contribution_stats(
        self,
        chapter: Chapter,
        start_date: datetime,
    ) -> dict[str, int]:
        """Calculate detailed contribution statistics for a chapter.

        Args:
            chapter: Chapter instance
            start_date: Start date for calculation

        Returns:
            Dictionary with commits, issues, pull requests, releases counts

        """
        stats = {
            "commits": 0,
            "issues": 0,
            "pull_requests": 0,
            "releases": 0,
            "total": 0,
        }

        if not chapter.owasp_repository:
            return stats

        repository = chapter.owasp_repository

        # Count commits
        stats["commits"] = Commit.objects.filter(
            repository=repository,
            created_at__gte=start_date,
        ).count()

        # Count issues
        stats["issues"] = Issue.objects.filter(
            repository=repository,
            created_at__gte=start_date,
        ).count()

        # Count pull requests
        stats["pull_requests"] = PullRequest.objects.filter(
            repository=repository,
            created_at__gte=start_date,
        ).count()

        # Count releases (exclude drafts)
        stats["releases"] = Release.objects.filter(
            repository=repository,
            published_at__gte=start_date,
            is_draft=False,
        ).count()

        # Calculate total
        stats["total"] = (
            stats["commits"] + stats["issues"] + stats["pull_requests"] + stats["releases"]
        )

        return stats

    def calculate_project_contribution_stats(
        self,
        project: Project,
        start_date: datetime,
    ) -> dict[str, int]:
        """Calculate detailed contribution statistics for a project.

        Args:
            project: Project instance
            start_date: Start date for calculation

        Returns:
            Dictionary with commits, issues, pull requests, releases counts

        """
        stats = {
            "commits": 0,
            "issues": 0,
            "pull_requests": 0,
            "releases": 0,
            "total": 0,
        }

        repositories = list(project.repositories.all())
        if project.owasp_repository:
            repositories.append(project.owasp_repository)

        repository_ids = [repo.id for repo in repositories if repo]

        if not repository_ids:
            return stats

        # Count commits
        stats["commits"] = Commit.objects.filter(
            repository_id__in=repository_ids,
            created_at__gte=start_date,
        ).count()

        # Count issues
        stats["issues"] = Issue.objects.filter(
            repository_id__in=repository_ids,
            created_at__gte=start_date,
        ).count()

        # Count pull requests
        stats["pull_requests"] = PullRequest.objects.filter(
            repository_id__in=repository_ids,
            created_at__gte=start_date,
        ).count()

        # Count releases (exclude drafts)
        stats["releases"] = Release.objects.filter(
            repository_id__in=repository_ids,
            published_at__gte=start_date,
            is_draft=False,
        ).count()

        # Calculate total
        stats["total"] = (
            stats["commits"] + stats["issues"] + stats["pull_requests"] + stats["releases"]
        )

        return stats

    def handle(self, *args, **options):
        """Execute the command."""
        entity_type = options["entity_type"]
        days = options["days"]
        key = options.get("key")
        offset = options["offset"]

        start_date = timezone.now() - timedelta(days=days)

        self.stdout.write(
            self.style.SUCCESS(
                f"Aggregating contributions from {start_date.date()} ({days} days back)",
            ),
        )

        if entity_type == "chapter":
            self._process_chapters(start_date, key, offset)
        elif entity_type == "project":
            self._process_projects(start_date, key, offset)

        self.stdout.write(self.style.SUCCESS("Done!"))

    def _process_chapters(self, start_date, key, offset):
        """Process chapters for contribution aggregation."""
        active_chapters = Chapter.objects.filter(is_active=True).order_by("id")

        if key:
            active_chapters = active_chapters.filter(key=key)

        active_chapters = active_chapters.select_related("owasp_repository")

        if offset:
            active_chapters = active_chapters[offset:]

        self.stdout.write(f"Processing {active_chapters.count()} chapters...")

        chapters = []
        for chapter in active_chapters:
            chapter.contribution_data = self.aggregate_chapter_contributions(chapter, start_date)
            chapter.contribution_stats = self.calculate_chapter_contribution_stats(
                chapter, start_date
            )
            chapters.append(chapter)

        if chapters:
            Chapter.bulk_save(chapters, fields=("contribution_data", "contribution_stats"))
            self.stdout.write(
                self.style.SUCCESS(f"Updated {active_chapters.count()} chapters"),
            )

    def _process_projects(self, start_date, key, offset):
        """Process projects for contribution aggregation."""
        active_projects = (
            Project.objects.filter(is_active=True)
            .order_by("id")
            .select_related("owasp_repository")
            .prefetch_related("repositories")
        )

        if key:
            active_projects = active_projects.filter(key=key)

        if offset:
            active_projects = active_projects[offset:]

        self.stdout.write(f"Processing {active_projects.count()} projects...")

        projects = []
        for project in active_projects:
            project.contribution_data = self.aggregate_project_contributions(project, start_date)
            project.contribution_stats = self.calculate_project_contribution_stats(
                project, start_date
            )
            projects.append(project)

        if projects:
            Project.bulk_save(projects, fields=("contribution_data", "contribution_stats"))
            self.stdout.write(self.style.SUCCESS(f"Updated {active_projects.count()} projects"))
