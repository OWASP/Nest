"""Management command to aggregate contributions for chapters and projects."""

from datetime import datetime, timedelta
from typing import Dict

from django.core.management.base import BaseCommand
from django.db.models import Q
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

    def aggregate_chapter_contributions(
        self,
        chapter: Chapter,
        start_date: datetime,
    ) -> Dict[str, int]:
        """Aggregate contributions for a chapter.

        Args:
            chapter: Chapter instance
            start_date: Start date for aggregation

        Returns:
            Dictionary mapping YYYY-MM-DD to contribution count

        """
        contribution_map = {}

        if not chapter.owasp_repository:
            return contribution_map

        repository = chapter.owasp_repository

        # Aggregate commits
        commits = Commit.objects.filter(
            repository=repository,
            created_at__gte=start_date,
        ).values_list("created_at", flat=True)

        for created_at in commits:
            if created_at:
                date_key = created_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

        # Aggregate issues
        issues = Issue.objects.filter(
            repository=repository,
            created_at__gte=start_date,
        ).values_list("created_at", flat=True)

        for created_at in issues:
            if created_at:
                date_key = created_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

        # Aggregate pull requests
        pull_requests = PullRequest.objects.filter(
            repository=repository,
            created_at__gte=start_date,
        ).values_list("created_at", flat=True)

        for created_at in pull_requests:
            if created_at:
                date_key = created_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

        # Aggregate releases (exclude drafts)
        releases = Release.objects.filter(
            repository=repository,
            published_at__gte=start_date,
            is_draft=False,
        ).values_list("published_at", flat=True)

        for published_at in releases:
            if published_at:
                date_key = published_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

        return contribution_map

    def aggregate_project_contributions(
        self,
        project: Project,
        start_date: datetime,
    ) -> Dict[str, int]:
        """Aggregate contributions for a project across all its repositories.

        Args:
            project: Project instance
            start_date: Start date for aggregation

        Returns:
            Dictionary mapping YYYY-MM-DD to contribution count

        """
        contribution_map = {}

        repositories = list(project.repositories.all())
        if project.owasp_repository:
            repositories.append(project.owasp_repository)

        repository_ids = [repo.id for repo in repositories if repo]

        if not repository_ids:
            return contribution_map

        # Aggregate commits
        commits = Commit.objects.filter(
            repository_id__in=repository_ids,
            created_at__gte=start_date,
        ).values_list("created_at", flat=True)

        for created_at in commits:
            if created_at:
                date_key = created_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

        # Aggregate issues
        issues = Issue.objects.filter(
            repository_id__in=repository_ids,
            created_at__gte=start_date,
        ).values_list("created_at", flat=True)

        for created_at in issues:
            if created_at:
                date_key = created_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

        # Aggregate pull requests
        pull_requests = PullRequest.objects.filter(
            repository_id__in=repository_ids,
            created_at__gte=start_date,
        ).values_list("created_at", flat=True)

        for created_at in pull_requests:
            if created_at:
                date_key = created_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

        # Aggregate releases (exclude drafts)
        releases = Release.objects.filter(
            repository_id__in=repository_ids,
            published_at__gte=start_date,
            is_draft=False,
        ).values_list("published_at", flat=True)

        for published_at in releases:
            if published_at:
                date_key = published_at.date().isoformat()
                contribution_map[date_key] = contribution_map.get(date_key, 0) + 1

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
            chapter_queryset = Chapter.objects.filter(is_active=True)

            if key:
                chapter_queryset = chapter_queryset.filter(key=key)

            if offset:
                chapter_queryset = chapter_queryset[offset:]

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

        # Process projects
        if entity_type in ["project", "both"]:
            project_queryset = Project.objects.filter(is_active=True)

            if key:
                project_queryset = project_queryset.filter(key=key)

            if offset:
                project_queryset = project_queryset[offset:]

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

        self.stdout.write(self.style.SUCCESS("Done!"))
