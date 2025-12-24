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

    def _get_repository_ids(self, entity):
        """Extract repository IDs from chapter or project."""
        repository_ids: set[int] = set()

        # Handle single owasp_repository.
        if hasattr(entity, "owasp_repository") and entity.owasp_repository:
            repository_ids.add(entity.owasp_repository.id)

        # Handle multiple repositories (for projects).
        if hasattr(entity, "repositories"):
            repository_ids.update([r.id for r in entity.repositories.all()])

        return list(repository_ids)

    def aggregate_contributions(self, entity, start_date: datetime) -> dict[str, int]:
        """Aggregate contributions for a chapter or project.

        Args:
            entity: Chapter or Project instance
            start_date: Start date for aggregation

        Returns:
            Dictionary mapping YYYY-MM-DD to contribution count

        """
        contribution_map: dict[str, int] = {}

        repository_ids = self._get_repository_ids(entity)
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
                created_at__gte=start_date,
                repository_id__in=repository_ids,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate pull requests.
        self._aggregate_contribution_dates(
            PullRequest.objects.filter(
                created_at__gte=start_date,
                repository_id__in=repository_ids,
            ),
            "created_at",
            contribution_map,
        )

        # Aggregate releases.
        self._aggregate_contribution_dates(
            Release.objects.filter(
                is_draft=False,
                published_at__gte=start_date,
                repository_id__in=repository_ids,
            ),
            "published_at",
            contribution_map,
        )

        return contribution_map

    def calculate_contribution_stats(self, entity, start_date: datetime) -> dict[str, int]:
        """Calculate contribution statistics for a chapter or project.

        Args:
            entity: Chapter or Project instance
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

        repository_ids = self._get_repository_ids(entity)
        if not repository_ids:
            return stats

        # Count commits.
        stats["commits"] = Commit.objects.filter(
            created_at__gte=start_date,
            repository_id__in=repository_ids,
        ).count()

        # Count issues.
        stats["issues"] = Issue.objects.filter(
            created_at__gte=start_date,
            repository_id__in=repository_ids,
        ).count()

        # Count pull requests.
        stats["pull_requests"] = PullRequest.objects.filter(
            created_at__gte=start_date,
            repository_id__in=repository_ids,
        ).count()

        # Count releases.
        stats["releases"] = Release.objects.filter(
            is_draft=False,
            published_at__gte=start_date,
            repository_id__in=repository_ids,
        ).count()

        stats["total"] = sum(
            (stats["commits"], stats["issues"], stats["pull_requests"], stats["releases"])
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
                f"Aggregating contributions since {start_date.date()} ({days} days back)",
            ),
        )

        if entity_type == "chapter":
            self._process_chapters(start_date, key, offset)
        elif entity_type == "project":
            self._process_projects(start_date, key, offset)

        self.stdout.write(self.style.SUCCESS("Done!"))

    def _process_chapters(self, start_date, key, offset):
        """Process chapters for contribution aggregation."""
        queryset = Chapter.objects.filter(is_active=True).order_by("id")

        if key:
            queryset = queryset.filter(key=key)

        queryset = queryset.select_related("owasp_repository")

        if offset:
            queryset = queryset[offset:]

        self._process_entities(queryset, start_date, Chapter)

    def _process_projects(self, start_date, key, offset):
        """Process projects for contribution aggregation."""
        queryset = (
            Project.objects.filter(is_active=True)
            .order_by("id")
            .select_related("owasp_repository")
            .prefetch_related("repositories")
        )

        if key:
            queryset = queryset.filter(key=key)

        if offset:
            queryset = queryset[offset:]

        self._process_entities(queryset, start_date, Project)

    def _process_entities(self, queryset, start_date, model_class):
        """Process entities (chapters or projects) for contribution aggregation."""
        entities = list(queryset)
        label = model_class._meta.verbose_name_plural
        total_count = len(entities)

        self.stdout.write(f"Processing {total_count} {label}...")

        for entity in entities:
            entity.contribution_data = self.aggregate_contributions(entity, start_date)
            entity.contribution_stats = self.calculate_contribution_stats(entity, start_date)

        if entities:
            model_class.bulk_save(entities, fields=("contribution_data", "contribution_stats"))
            self.stdout.write(self.style.SUCCESS(f"Updated {total_count} {label}"))
