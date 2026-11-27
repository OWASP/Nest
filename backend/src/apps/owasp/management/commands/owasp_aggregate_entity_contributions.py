"""Management command to aggregate contributions for chapters and projects."""

from argparse import ArgumentParser
from datetime import UTC, datetime, timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Count, QuerySet
from django.db.models.functions import TruncDate
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

    def add_arguments(self, parser: ArgumentParser) -> None:
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
        queryset: QuerySet[Any],
        date_field: str,
        contribution_map: dict[str, int],
    ) -> int:
        """Add database-grouped UTC daily counts and return their category total."""
        daily_counts = (
            queryset.annotate(day=TruncDate(date_field, tzinfo=UTC))
            .values("day")
            .annotate(count=Count("pk"))
            .order_by()
        )
        total = 0
        for row in daily_counts:
            date_key = row["day"].isoformat()
            count = row["count"]
            contribution_map[date_key] = contribution_map.get(date_key, 0) + count
            total += count
        return total

    def _get_repository_ids(self, entity: Chapter | Project) -> list[int]:
        """Extract repository IDs from chapter or project."""
        repository_ids: set[int] = set()

        # Handle single owasp_repository.
        if hasattr(entity, "owasp_repository") and entity.owasp_repository:
            repository_ids.add(entity.owasp_repository.id)

        # Handle multiple repositories (for projects).
        if hasattr(entity, "repositories"):
            repository_ids.update([r.id for r in entity.repositories.all()])

        return list(repository_ids)

    def aggregate_contributions(
        self, entity: Chapter | Project, start_at: datetime, end_at: datetime
    ) -> tuple[dict[str, int], dict[str, int | str]]:
        """Build daily data and summary statistics from the same bounded UTC groups."""
        contribution_map: dict[str, int] = {}
        stats = {"commits": 0, "issues": 0, "pull_requests": 0, "releases": 0}
        repository_ids = self._get_repository_ids(entity)

        if repository_ids:
            for model, category, date_field in (
                (Commit, "commits", "created_at"),
                (Issue, "issues", "created_at"),
                (PullRequest, "pull_requests", "created_at"),
                (Release, "releases", "published_at"),
            ):
                filters: dict[str, Any] = {
                    "repository_id__in": repository_ids,
                    f"{date_field}__gte": start_at,
                    f"{date_field}__lte": end_at,
                }
                if model is Release:
                    filters["is_draft"] = False
                stats[category] = self._aggregate_contribution_dates(
                    model.objects.filter(**filters), date_field, contribution_map
                )

        return contribution_map, {
            **stats,
            "total": sum(stats.values()),
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        }

    def handle(self, *args: Any, **options: Any) -> None:
        """Execute the command."""
        entity_type = options["entity_type"]
        days = options["days"]
        key = options.get("key")
        offset = options["offset"]

        end_at = timezone.now().astimezone(UTC)
        start_at = end_at - timedelta(days=days)

        self.stdout.write(
            self.style.SUCCESS(
                f"Aggregating contributions from {start_at.isoformat()} to "
                f"{end_at.isoformat()} ({days} days back)",
            ),
        )

        if entity_type == "chapter":
            self._process_chapters(start_at, end_at, key, offset)
        elif entity_type == "project":
            self._process_projects(start_at, end_at, key, offset)

        self.stdout.write(self.style.SUCCESS("Done!"))

    def _process_chapters(
        self, start_at: datetime, end_at: datetime, key: str | None, offset: int
    ) -> None:
        """Process chapters for contribution aggregation."""
        queryset = Chapter.objects.filter(is_active=True).order_by("id")

        if key:
            queryset = queryset.filter(key=key)

        queryset = queryset.select_related("owasp_repository")

        if offset:
            queryset = queryset[offset:]

        self._process_entities(queryset, start_at, end_at, Chapter)

    def _process_projects(
        self, start_at: datetime, end_at: datetime, key: str | None, offset: int
    ) -> None:
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

        self._process_entities(queryset, start_at, end_at, Project)

    def _process_entities(
        self,
        queryset: QuerySet[Chapter] | QuerySet[Project],
        start_at: datetime,
        end_at: datetime,
        model_class: type[Chapter] | type[Project],
    ) -> None:
        """Process entities (chapters or projects) for contribution aggregation."""
        entities = list(queryset)
        label = model_class._meta.verbose_name_plural
        total_count = len(entities)

        self.stdout.write(f"Processing {total_count} {label}...")

        for entity in entities:
            entity.contribution_data, entity.contribution_stats = self.aggregate_contributions(
                entity, start_at, end_at
            )

        if entities:
            fields = ("contribution_data", "contribution_stats")
            if model_class is Chapter:
                Chapter.bulk_save(entities, fields=fields)
            else:
                Project.bulk_save(entities, fields=list(fields))
            self.stdout.write(self.style.SUCCESS(f"Updated {total_count} {label}"))
