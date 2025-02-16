"""GitHub app pull requests managers."""

from datetime import timedelta as td

from django.db import models
from django.utils import timezone


class OpenPullRequestManager(models.Manager):
    """Open pull requests."""

    def get_queryset(self):
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
