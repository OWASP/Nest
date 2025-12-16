"""GitHub app issue managers."""

from datetime import timedelta as td

from django.db import models
from django.db.models import Q
from django.utils import timezone


class OpenIssueManager(models.Manager):
    """Open issues."""

    def get_queryset(self) -> models.QuerySet:
        """Get queryset."""
        return (
            super()
            .get_queryset()
            .select_related(
                "repository",
            )
            .prefetch_related(
                "assignees",
            )
            .filter(
                created_at__gte=timezone.now() - td(days=90),
                repository__project__isnull=False,
                state="open",
            )
        )

    @property
    def assignable(self) -> models.QuerySet:
        """Return assignable issues.

        Includes all unassigned issues and assigned issues with no activity within 90 days.
        """
        return self.get_queryset().filter(
            Q(assignees__isnull=True)
            | Q(
                assignees__isnull=False,
                updated_at__lte=timezone.now() - td(days=30),
            )
        )

    @property
    def without_summary(self) -> models.QuerySet:
        """Return issues without summary."""
        return self.get_queryset().filter(summary="")


class SnapshotIssueManager(models.Manager):
    """Issues for snapshot processing."""

    def get_queryset(self):
        """Get queryset of issues with non-empty repositories.

        Filters out issues from empty repositories to ensure data integrity.
        """
        return (
            super()
            .get_queryset()
            .select_related("repository")
            .filter(repository__is_empty=False)
        )
