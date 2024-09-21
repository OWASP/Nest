"""GitHub app issue managers."""

from datetime import timedelta as td

from django.db import models
from django.db.models import Q
from django.utils import timezone


class OpenIssueManager(models.Manager):
    """Open issues."""

    def get_queryset(self):
        """Get queryset."""
        return (
            super()
            .get_queryset()
            .select_related(
                "repository",
            )
            .filter(
                repository__project__isnull=False,
                state="open",
            )
        )

    @property
    def assignable(self):
        """Return assignable issues.

        Includes all unassigned issues and assigned issues with no activity within 90 days.
        """
        return self.get_queryset().filter(
            Q(assignees__isnull=True)
            | Q(
                assignees__isnull=False,
                updated_at__lte=timezone.now() - td(days=90),
            )
        )

    @property
    def without_summary(self):
        """Return issues without summary."""
        return self.get_queryset().filter(summary="")
