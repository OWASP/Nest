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
            type=str,
            choices=["chapter", "project", "both"],
            default="both",
            help="Entity type to aggregate: chapter, project, or both",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=365,
            help="Number of days to look back for contributions (default: 365)",
        )
        parser.add_argument(
            "--key",
            type=str,
            help="Specific chapter or project key to aggregate",
        )
        parser.add_argument(
            "--offset",
            type=int,
            default=0,
            help="Skip the first N entities",
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
        dates = queryset.values_list(date_field, flat=True)
        for date_value in dates:
            if date_value:
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

        # Aggregate commits
        self._aggregate_contribution_dates(
            Commit.objects.filter(
                repository=repository,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate issues
        self._aggregate_contribution_dates(
            Issue.objects.filter(
                repository=repository,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate pull requests
        self._aggregate_contribution_dates(
            PullRequest.objects.filter(
                repository=repository,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate releases (exclude drafts)
        self._aggregate_contribution_dates(
            Release.objects.filter(
                repository=repository,
                published_at__gte=start_date,
                is_draft=False,
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

        repositories = list(project.repositories.all())
        if project.owasp_repository:
            repositories.append(project.owasp_repository)

        repository_ids = [repo.id for repo in repositories if repo]

        if not repository_ids:
            return contribution_map

        # Aggregate commits
        self._aggregate_contribution_dates(
            Commit.objects.filter(
                repository_id__in=repository_ids,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate issues
        self._aggregate_contribution_dates(
            Issue.objects.filter(
                repository_id__in=repository_ids,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate pull requests
        self._aggregate_contribution_dates(
            PullRequest.objects.filter(
                repository_id__in=repository_ids,
                created_at__gte=start_date,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate releases (exclude drafts)
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

        # Process chapters
        if entity_type in ["chapter", "both"]:
            self._process_chapters(start_date, key, offset)

        # Process projects
        if entity_type in ["project", "both"]:
            self._process_projects(start_date, key, offset)

        self.stdout.write(self.style.SUCCESS("Done!"))

    def _process_chapters(self, start_date, key, offset):
        """Process chapters for contribution aggregation."""
        chapter_queryset = Chapter.objects.filter(is_active=True)

        if key:
            chapter_queryset = chapter_queryset.filter(key=key)

        if offset:
            chapter_queryset = chapter_queryset[offset:]

        chapter_queryset = chapter_queryset.select_related("owasp_repository")
        chapters = list(chapter_queryset)
        self.stdout.write(f"Processing {len(chapters)} chapters...")

        for chapter in chapters:
            contribution_data = self.aggregate_chapter_contributions(
                chapter,
                start_date,
            )
            chapter.contribution_data = contribution_data

        if chapters:
            Chapter.bulk_save(chapters, fields=("contribution_data",))
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated {len(chapters)} chapters"),
            )

    def _process_projects(self, start_date, key, offset):
        """Process projects for contribution aggregation."""
        project_queryset = Project.objects.filter(is_active=True)

        if key:
            project_queryset = project_queryset.filter(key=key)

        if offset:
            project_queryset = project_queryset[offset:]

        project_queryset = project_queryset.select_related(
            "owasp_repository"
        ).prefetch_related("repositories")
        projects = list(project_queryset)
        self.stdout.write(f"Processing {len(projects)} projects...")

        for project in projects:
            contribution_data = self.aggregate_project_contributions(
                project,
                start_date,
            )
            project.contribution_data = contribution_data

        if projects:
            Project.bulk_save(projects, fields=("contribution_data",))
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated {len(projects)} projects"),
            )
